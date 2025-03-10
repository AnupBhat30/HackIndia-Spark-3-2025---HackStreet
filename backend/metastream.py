from hyperon import MeTTa
import google.generativeai as genai
import streamlit as st
import re
from collections import defaultdict

# ==============================================================================
# 1. SET PAGE CONFIG FIRST (MUST BE THE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="AI Loan Advisor", page_icon="💼", layout="wide")

# ==============================================================================
# Configure Gemini API
genai.configure(api_key="AIzaSyCUd4ZMonA-qcB_1sLu0gNgj_VYXkbQo1g")
model = genai.GenerativeModel('gemini-2.0-flash')

# ==============================================================================
# Cache MeTTa instance and database loading
@st.cache_resource
def load_metta():
    metta = MeTTa()
    try:
        with open("/Users/anupbhat/hacker/db.metta", 'r') as f:
            db_content = f.read()
        metta.run(db_content)
    except Exception as e:
        st.error(f"Failed to load database: {str(e)}")
        raise
    return metta

metta = load_metta()

# ==============================================================================
# Helper Functions
def run_query(query):
    """Run MeTTa query using Python API directly."""
    try:
        return metta.run(f"!{query}")
    except Exception as e:
        st.error(f"MeTTa query failed: {str(e)}")
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
    user_input_lower = user_input.lower()
    
    # Lender queries
    if ("which lender" in user_input_lower or "what lender" in user_input_lower) and any(x in user_input_lower for x in ["offer", "provide"]):
        for loan_type in ["education", "personal", "housing", "refugee", "disaster", "medical", "small business", 
                         "agricultural", "women empowerment", "accident"]:
            if loan_type in user_input_lower:
                formatted_loan = loan_type.replace(" ", "-").title()
                if not formatted_loan.endswith("-Loan"):
                    formatted_loan += "-Loan"
                
                query = f"(match &self (Lender $lender Offers {formatted_loan}) ($lender))"
                result = run_query(query)
                
                if result:
                    extracted_values = extract_values(result)
                    if extracted_values:
                        lenders = []
                        for lender_id in extracted_values:
                            if lender_id and len(lender_id) > 0:
                                name_query = f"(match &self (Lender {lender_id[0]} Has-Name $name) ($name))"
                                name_result = run_query(name_query)
                                extracted_name = extract_values(name_result)
                                lenders.append(extracted_name[0][0] if extracted_name else lender_id[0].replace("-", " "))
                        
                        if lenders:
                            return f"The following lenders offer {loan_type.title()} Loans: {', '.join(lenders)}."
                return f"Sorry, I couldn't find any lenders offering {loan_type.title()} Loans in our database."
    
    # Interest rate queries
    if "interest rate" in user_input_lower:
        for loan_type in ["education", "personal", "housing", "refugee", "disaster", "medical", 
                          "small business", "agricultural", "women empowerment"]:
            if loan_type in user_input_lower:
                formatted_loan = loan_type.replace(" ", "-").title()
                if not formatted_loan.endswith("-Loan"):
                    formatted_loan += "-Loan"
                
                query = f"(match &self (Loan-Types {formatted_loan} Has-InterestRate $rate) ($rate))"
                result = run_query(query)
                extracted = extract_values(result)
                if extracted:
                    return f"The interest rate for {loan_type.title()} Loans is {extracted[0][0]}."
    
    # Eligibility queries
    if "eligible" in user_input_lower or "qualify" in user_input_lower:
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
            credit_result = extract_values(run_query(f"(match &self ({person} Has-CreditScore $score) ($score))"))
            income_result = extract_values(run_query(f"(match &self ({person} Has-Income $income) ($income))"))
            age_result = extract_values(run_query(f"(match &self ({person} Has-Age $age) ($age))"))
            
            req_credit_result = extract_values(run_query(f"(match &self (Loan-Types {loan_type} Has-CreditScoreRequired $req) ($req))"))
            req_income_result = extract_values(run_query(f"(match &self (Loan-Types {loan_type} Has-MinIncome $req) ($req))"))
            req_age_result = extract_values(run_query(f"(match &self (Loan-Types {loan_type} Has-AgeLimit $req) ($req))"))
            
            if all([credit_result, income_result, age_result, req_credit_result, req_income_result, req_age_result]):
                meets_credit = int(credit_result[0][0]) >= int(req_credit_result[0][0])
                meets_income = int(income_result[0][0]) >= int(req_income_result[0][0])
                meets_age = int(age_result[0][0]) <= int(req_age_result[0][0])
                eligible = meets_credit and meets_income and meets_age
                
                response = f"""**Eligibility check for {person} and {clean_loan_name(loan_type)}:**
                
**Profile:**
- Credit Score: {credit_result[0][0]}
- Income: {income_result[0][0]}
- Age: {age_result[0][0]}

**Requirements:**
- Required Credit Score: {req_credit_result[0][0]}
- Minimum Income: {req_income_result[0][0]}
- Maximum Age: {req_age_result[0][0]}

**Results:**
- Credit Score: {'✅ Meets' if meets_credit else '❌ Does not meet'}
- Income: {'✅ Meets' if meets_income else '❌ Does not meet'}
- Age: {'✅ Meets' if meets_age else '❌ Does not meet'}

**OVERALL:** {'🟢 ELIGIBLE' if eligible else '🔴 NOT ELIGIBLE'}"""
                return response
                
    # Fall back to Gemini
    return generate_response_from_gemini(user_input)

def generate_response_from_gemini(question):
    """Generate response using Gemini for general questions."""
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
        return f"**General Information:**\n\n{response.text.strip()}"
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# ==============================================================================
# Streamlit UI
# Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your AI Loan Advisor. Ask me about lenders, interest rates, eligibility, or any loan-related questions!"}]

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Ask your loan question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.spinner("Analyzing your query..."):
        response = process_user_query(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar Controls
with st.sidebar:
    st.title("Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. Ask me anything about loans!"}]
    st.markdown("---")
    st.markdown("**Note:** This system uses synthetic data from our MeTTa database and Gemini AI for general financial knowledge.")