from hyperon import MeTTa
import google.generativeai as genai
import re
from collections import defaultdict

# Configure Gemini API
genai.configure(api_key="AIzaSyCUd4ZMonA-qcB_1sLu0gNgj_VYXkbQo1g")
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize MeTTa instance
metta = MeTTa()

# Load the database file only once
def load_metta_database():
    """Load the MeTTa database file."""
    try:
        with open("/Users/anupbhat/hacker/db.metta", 'r') as f:
            db_content = f.read()
        metta.run(db_content)
        print("[INFO] Successfully loaded db.metta into MeTTa.")
    except Exception as e:
        print(f"[ERROR] Failed to load db.metta: {str(e)}")
        exit(1)

def run_query(query):
    """Run MeTTa query using Python API directly."""
    print(f"[DEBUG] Executing MeTTa query: {query}")
    try:
        result = metta.run(f"!{query}")
        print(f"[DEBUG] Query result: {result}")
        return result
    except Exception as e:
        print(f"[ERROR] MeTTa query failed: {str(e)}")
        return None

def extract_values(result):
    """Extract values from MeTTa result objects."""
    if not result:
        return []
    
    values = []
    for item in result:
        if item and len(item) > 0:
            atoms = item[0].get_children()
            values.append([str(atom) for atom in atoms])
    return values

def clean_loan_name(loan):
    """Format loan IDs for display"""
    return loan.replace('-Loan', ' Loan').replace('-', ' ')

def process_user_query(user_input):
    """Process user query with direct handling for common patterns."""
    print(f"[INFO] Processing query: {user_input}")
    
    user_input_lower = user_input.lower()
    
    # Direct handling for lender queries
    if ("which lender" in user_input_lower or "what lender" in user_input_lower) and any(x in user_input_lower for x in ["offer", "provide"]):
        for loan_type in ["education", "personal", "housing", "refugee", "disaster", "medical", "small business", 
                         "agricultural", "women empowerment", "accident"]:
            if loan_type in user_input_lower:
                # Format loan type correctly
                formatted_loan = loan_type.replace(" ", "-").title()
                if not formatted_loan.endswith("-Loan"):
                    formatted_loan += "-Loan"
                
                # Query directly using MeTTa API
                query = f"(match &self (Lender $lender Offers {formatted_loan}) ($lender))"
                result = run_query(query)
                
                if result:
                    extracted_values = extract_values(result)
                    if extracted_values:
                        lenders = []
                        for lender_id in extracted_values:
                            if lender_id and len(lender_id) > 0:
                                # Get lender's name
                                name_query = f"(match &self (Lender {lender_id[0]} Has-Name $name) ($name))"
                                name_result = run_query(name_query)
                                extracted_name = extract_values(name_result)
                                
                                if extracted_name and len(extracted_name) > 0:
                                    lenders.append(extracted_name[0][0])
                                else:
                                    lenders.append(lender_id[0].replace("-", " "))
                        
                        if lenders:
                            return f"The following lenders offer {loan_type.title()} Loans: {', '.join(lenders)}."
                
                # Fall back if no results found
                return f"Sorry, I couldn't find any lenders offering {loan_type.title()} Loans in our database."
    
    # ===== Additional query patterns can be handled here =====
    
    # Interest rate queries
    if "interest rate" in user_input_lower and any(loan_type in user_input_lower for loan_type in 
                                                  ["education", "personal", "housing", "refugee", "disaster", 
                                                   "medical", "small business", "agricultural", "women"]):
        for loan_type in ["education", "personal", "housing", "refugee", "disaster", "medical", 
                          "small business", "agricultural", "women empowerment"]:
            if loan_type in user_input_lower:
                formatted_loan = loan_type.replace(" ", "-").title()
                if not formatted_loan.endswith("-Loan"):
                    formatted_loan += "-Loan"
                
                query = f"(match &self (Loan-Types {formatted_loan} Has-InterestRate $rate) ($rate))"
                result = run_query(query)
                extracted = extract_values(result)
                
                if extracted and len(extracted) > 0:
                    return f"The interest rate for {loan_type.title()} Loans is {extracted[0][0]}."
    
    # Eligibility queries
    if "eligible" in user_input_lower or "qualify" in user_input_lower:
        # Check if it's about John or Mary (people defined in db)
        person = None
        loan_type = None
        
        if "john" in user_input_lower:
            person = "John"
        elif "mary" in user_input_lower:
            person = "Mary"
            
        for loan_name in ["education", "personal", "housing", "refugee", "disaster", "medical", 
                          "small business", "agricultural", "women empowerment"]:
            if loan_name in user_input_lower:
                loan_type = loan_name.replace(" ", "-").title()
                if not loan_type.endswith("-Loan"):
                    loan_type += "-Loan"
                break
                
        if person and loan_type:
            # Get person's profile
            credit_query = f"(match &self ({person} Has-CreditScore $score) ($score))"
            income_query = f"(match &self ({person} Has-Income $income) ($income))"
            age_query = f"(match &self ({person} Has-Age $age) ($age))"
            
            credit_result = extract_values(run_query(credit_query))
            income_result = extract_values(run_query(income_query))
            age_result = extract_values(run_query(age_query))
            
            # Get loan requirements
            req_credit_query = f"(match &self (Loan-Types {loan_type} Has-CreditScoreRequired $req) ($req))"
            req_income_query = f"(match &self (Loan-Types {loan_type} Has-MinIncome $req) ($req))"
            req_age_query = f"(match &self (Loan-Types {loan_type} Has-AgeLimit $req) ($req))"
            
            req_credit_result = extract_values(run_query(req_credit_query))
            req_income_result = extract_values(run_query(req_income_query))
            req_age_result = extract_values(run_query(req_age_query))
            
            if credit_result and income_result and age_result and req_credit_result and req_income_result and req_age_result:
                # Compare values
                meets_credit = int(credit_result[0][0]) >= int(req_credit_result[0][0])
                meets_income = int(income_result[0][0]) >= int(req_income_result[0][0])
                meets_age = int(age_result[0][0]) <= int(req_age_result[0][0])
                eligible = meets_credit and meets_income and meets_age
                
                # Format response
                response = f"Eligibility check for {person} and {clean_loan_name(loan_type)}:\n\n"
                response += "Profile:\n"
                response += f"- Credit Score: {credit_result[0][0]}\n"
                response += f"- Income: {income_result[0][0]}\n"
                response += f"- Age: {age_result[0][0]}\n\n"
                
                response += "Requirements:\n"
                response += f"- Required Credit Score: {req_credit_result[0][0]}\n"
                response += f"- Minimum Income: {req_income_result[0][0]}\n"
                response += f"- Maximum Age: {req_age_result[0][0]}\n\n"
                
                response += "Results:\n"
                response += f"- Credit Score: {'Meets' if meets_credit else 'Does not meet'} requirement\n"
                response += f"- Income: {'Meets' if meets_income else 'Does not meet'} requirement\n"
                response += f"- Age: {'Meets' if meets_age else 'Does not meet'} requirement\n\n"
                
                response += f"OVERALL: {'ELIGIBLE' if eligible else 'NOT ELIGIBLE'} for {clean_loan_name(loan_type)}"
                
                return response
                
    # If no direct handling matched, fall back to Gemini
    return generate_response_from_gemini(user_input)

def generate_response_from_gemini(question):
    """Generate response using Gemini when we don't have data in MeTTa."""
    try:
        prompt = f"""
You are an AI-powered financial assistant designed to assist users with loan-related queries using your general knowledge and advanced analytical capabilities. Your goal is to provide friendly, concise, accurate, and fact-enriched answers. If you're unsure of an answer, say so rather than making up information, and specify that your responses are based on general financial knowledge, not specific databases. Follow these detailed capabilities and guidelines to respond effectively:

1. **Tailor-Made Loan Offer and Personalized Loan Matching**
   - **Definition**: Assess user-provided financial information (e.g., credit score, income) to recommend loan programs that match their borrowing needs and repayment capacity, including mortgage eligibility where applicable.
   - **Example**: For a user with a 700 credit score and $60,000 annual income, suggest a 30-year mortgage at 5% interest with monthly payments of $1,200; for a 550 score, recommend a secured loan at 10% with lower payments.
   - **Guidance**: Ask for credit or income details if needed, then tailor suggestions (e.g., fixed-rate loans for stability, adjustable-rate for risk-takers).

2. **Cost Dissection and Comparative Analysis of Loans Using Artificial Intelligence**
   - **Definition**: Analyze loan options beyond interest rates, calculating total repayment amounts including shadow costs (indirect costs like opportunity cost or risk premiums), prepayment charges, and break-even penalty costs.
   - **Example**: Compare Loan A (5% interest, $500 origination fee, 2% prepayment penalty) vs. Loan B (6% interest, no fees) over 10 years, showing Loan A totals $15,000 vs. Loan B's $14,400 due to lower hidden costs.
   - **Guidance**: Use AI-like reasoning to break down costs, explain terms (e.g., APR as annual percentage rate), and highlight the cheaper long-term option.

3. **Clause Detection and Legal Visibility for AI-Powered Products**
   - **Definition**: Simplify loan agreements into basic terms and identify risky clauses, such as floating interest charges, foreclosure penalties, or other hidden fees, to enhance user understanding.
   - **Example**: Flag a clause with a floating rate starting at 4% but rising to 8%, or a 5% penalty for early repayment within 5 years, explaining impacts in simple language (e.g., 'This could raise your payments by $200 monthly').
   - **Guidance**: Translate jargon (e.g., 'foreclosure' as 'losing your home') and warn about high-risk terms with clear implications.

4. **Targeted Loan Assistance for Vulnerable Groups**
   - **Definition**: Offer customized loan counseling for students, refugees, and emergency victims, ensuring access to government-sponsored loans or minimal-risk aid programs.
   - **Example**: For a student, recommend federal loans at 5.5% with income-driven repayment; for a refugee, suggest emergency housing loans with no interest for the first year.
   - **Guidance**: Identify user group (e.g., 'Are you a student?'), then provide specific, accessible options with eligibility details.

5. **Financial Planning & Repayment Forecasting**
   - **Definition**: Estimate future earnings to ensure loan repayment avoids bankruptcy, assessing impacts of postponed payments or early repayments on total costs.
   - **Example**: For a $50,000 income, suggest $500 monthly payments fit a $20,000 loan, noting a 6-month payment delay increases interest by $600 but eases short-term cash flow.
   - **Guidance**: Ask for income or loan details, then forecast budgets and payment scenarios, advising on trade-offs (e.g., early repayment saves interest).

**General Guidelines**:
- Be friendly and approachable (e.g., 'Happy to help with your loan questions!').
- Provide definitions for financial terms (e.g., 'APR is the yearly cost of borrowing') and contextual references (e.g., 'Typical mortgage rates in 2025 are around 5-6%').
- Enrich answers with facts where possible (e.g., 'Average prepayment penalties are 2-5%').
- If a question falls outside these capabilities, say: 'I'm not sure about that, but I can help with loans and repayment planning!'
- Specify: 'This is general financial information based on my knowledge as of March 10, 2025, not tied to a specific database.'

**Question**: {question}
Answer based on the above capabilities and guidelines, tailoring your response to the user's query.
"""
        
        response = model.generate_content(prompt)
        return f"[General Info] {response.text.strip()}"
    except Exception as e:
        print(f"[ERROR] Error generating response from Gemini: {str(e)}")
        return f"I'm sorry, I couldn't generate a response at this time. Error: {str(e)}"

# Main function
def main():
    # Load MeTTa database at startup
    load_metta_database()
    
    print("Loan Advisor: Hey there! I'm your loan guru, ready to dive into all things loans with you. What's up?")
    
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Loan Advisor: Catch you later! Hope I shed some light on your loan questions!")
                break
            
            response = process_user_query(user_input)
            print(f"Loan Advisor: {response}")
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()