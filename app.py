from io import BytesIO
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date 

from database import (
    create_table,
    create_user,
    authenticate_user,
    add_transaction,
    get_transactions,
    set_monthly_budget,
    get_monthly_budget,
    update_transaction,
    delete_transaction
)

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# --------------------------------
# PREMIUM DARK THEME
# --------------------------------

st.markdown("""
<style>
/* App background and default text */
.stApp {
    background: #0B1120;
    color: #E5E7EB;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings and text */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeader"],
[data-testid="stMarkdownContainer"] p,
.stCaption {
    color: #E5E7EB !important;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

h2, h3 {
    font-weight: 700 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #101A2C;
    border-right: 1px solid #263449;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #151F32;
    border: 1px solid #263449;
    padding: 18px 20px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] p {
    color: #A8B4C7 !important;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-weight: 750 !important;
}

[data-testid="stMetricDelta"] {
    font-weight: 600;
}

/* Forms and containers */
[data-testid="stForm"],
[data-testid="stExpander"] {
    background: #111C2E;
    border: 1px solid #263449;
    border-radius: 14px;
    padding: 14px;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] {
    background-color: #172338 !important;
    color: #F8FAFC !important;
    border-color: #35445C !important;
    border-radius: 8px !important;
}

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label,
.stTextArea label,
.stCheckbox label,
.stRadio label {
    color: #CBD5E1 !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: #172338 !important;
    color: #F8FAFC !important;
}

[data-baseweb="menu"] *,
[role="option"] {
    color: #F8FAFC !important;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button,
.stDownloadButton button {
    background: #2563EB;
    color: #FFFFFF !important;
    border: 1px solid #3B82F6;
    border-radius: 9px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover,
.stDownloadButton button:hover {
    background: #1D4ED8;
    border-color: #60A5FA;
    color: #FFFFFF !important;
}

/* Dataframes */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #263449;
    border-radius: 10px;
    overflow: hidden;
}

/* Progress bar */
[data-testid="stProgressBar"] > div > div {
    background: #22C55E;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #263449 !important;
}

/* Download button text */
.stDownloadButton button p {
    color: #FFFFFF !important;
}

/* Keep icons and labels legible */
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    color: #CBD5E1;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# APPLICATION HEADER
# --------------------------------

st.title("💰 Smart Expense Tracker")
st.markdown("### Manage your money. Track your spending. Save smarter.")
st.caption("Your personal financial management dashboard")

# --------------------------------
# DATABASE INITIALIZATION
# --------------------------------

create_table()

# --------------------------------
# USER AUTHENTICATION
# --------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

if st.session_state.user_id is None:
    st.title("🔐 Welcome to Smart Expense Tracker")
    st.write("Sign in to access your personal financial dashboard, or create a new account.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("Login", use_container_width=True)

        if login_submit:
            result = authenticate_user(login_username.strip(), login_password)
            if result:
                st.session_state.user_id = result["id"]
                st.session_state.username = result["username"]
                st.rerun()
            else:
                st.error("Incorrect username or password. Please try again.")

    with signup_tab:
        with st.form("signup_form"):
            new_username = st.text_input("Choose a username", key="signup_username")
            new_password = st.text_input("Create a password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
            signup_submit = st.form_submit_button("Create Account", use_container_width=True)

        if signup_submit:
            clean_username = new_username.strip()
            if len(clean_username) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(new_password) < 8:
                st.error("Password must contain at least 8 characters.")
            elif new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                success, message = create_user(clean_username, new_password)
                if success:
                    st.success("Account created! You can now log in using your credentials.")
                else:
                    st.error(message)

    st.info("Each account has its own transactions and monthly budgets.")
    st.stop()

user_id = st.session_state.user_id

with st.sidebar:
    st.success(f"Logged in as **{st.session_state.username}**")
    if st.button("Log out", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

# --------------------------------
# APPLICATION TITLE
# --------------------------------

st.title("💰 Personal Expense Tracker")

st.write("Welcome! Manage your income and expenses in one place.")

# --------------------------------
# FETCH TRANSACTIONS
# --------------------------------

df = get_transactions(user_id)

# --------------------------------
# CALCULATE INCOME AND EXPENSES
# --------------------------------

if not df.empty:

    total_income = df[df["type"] == "Income"]["amount"].sum()

    total_expenses = df[df["type"] == "Expense"]["amount"].sum()

else:

    total_income = 0
    total_expenses = 0

balance = total_income - total_expenses

st.divider()
# --------------------------------
# MONTHLY BUDGET MANAGEMENT
# --------------------------------

st.divider()

st.subheader("🎯 Monthly Budget Management")

# Get current month
current_month = date.today().strftime("%Y-%m")

# Retrieve saved budget
current_budget = get_monthly_budget(current_month, user_id)

# Calculate current month's expenses
if not df.empty:

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    current_month_expenses = df[
        (df["type"] == "Expense") &
        (df["date"].dt.strftime("%Y-%m") == current_month)
    ]["amount"].sum()

else:

    current_month_expenses = 0

# Budget setting form
with st.form("budget_form"):

    new_budget = st.number_input(
        "Set Your Monthly Budget (₹)",
        min_value=0.0,
        value=float(current_budget),
        step=500.0
    )

    budget_submit = st.form_submit_button(
        "Save Monthly Budget"
    )

    if budget_submit:

        if new_budget > 0:

            set_monthly_budget(
                current_month,
                new_budget,
                user_id
            )

            st.success("Monthly budget saved successfully!")

            st.rerun()

        else:

            st.warning("Please enter a budget greater than zero.")

# Display budget information
if current_budget > 0:

    remaining_budget = current_budget - current_month_expenses

    percentage_used = (
        current_month_expenses / current_budget
    ) * 100

    st.write("### Your Budget Progress")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Monthly Budget",
            f"₹{current_budget:,.2f}"
        )

    with col2:
        st.metric(
            "Spent This Month",
            f"₹{current_month_expenses:,.2f}"
        )

    with col3:
        st.metric(
            "Budget Remaining",
            f"₹{remaining_budget:,.2f}"
        )

    # Progress bar
    st.progress(
        min(percentage_used / 100, 1.0)
    )

    st.write(
        f"Budget Used: {percentage_used:.1f}%"
    )

    # Spending alerts
    if percentage_used >= 100:

        st.error(
            "🚨 Budget Exceeded! "
            "You have spent more than your monthly budget."
        )

    elif percentage_used >= 80:

        st.warning(
            "⚠️ You have used 80% or more of your budget. "
            "Control your spending!"
        )

    else:

        st.success(
            "✅ You are within your monthly budget. Keep it up!"
        )

else:

    st.info(
        "Set your monthly budget to start tracking your spending."
    )


# --------------------------------
# DASHBOARD
# --------------------------------

st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Income",
        value=f"₹{total_income:,.2f}"
    )

with col2:
    st.metric(
        label="Total Expenses",
        value=f"₹{total_expenses:,.2f}"
    )

with col3:
    st.metric(
        label="Remaining Balance",
        value=f"₹{balance:,.2f}"
    )
st.divider()
# --------------------------------
# ADD NEW TRANSACTION
# --------------------------------

st.divider()

st.subheader("➕ Add New Transaction")

with st.form("transaction_form", clear_on_submit=True):

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Expense", "Income"]
    )

    amount = st.number_input(
        "Enter Amount (₹)",
        min_value=1.0,
        step=10.0
    )

    category = st.selectbox(
        "Select Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Salary",
            "Other"
        ]
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch at college"
    )

    date = st.date_input("Transaction Date")

    submit = st.form_submit_button("Add Transaction")

    if submit:

        add_transaction(
            transaction_type,
            amount,
            category,
            description,
            date,
            user_id
        )

        st.success("Transaction saved successfully!")

        st.rerun()
st.divider()
       
        # --------------------------------
# EXPENSE ANALYTICS
# --------------------------------

st.divider()

st.subheader("📊 Expense Analytics")

# Fetch transaction data
analytics_df = get_transactions(user_id)

if not analytics_df.empty:

    # Convert date column into datetime format
    analytics_df["date"] = pd.to_datetime(
        analytics_df["date"],
        errors="coerce"
    )

    # Remove rows with invalid dates
    analytics_df = analytics_df.dropna(subset=["date"])

    if not analytics_df.empty:

        # Separate expense transactions
        expense_df = analytics_df[
            analytics_df["type"] == "Expense"
        ]

        # Two columns for charts
        chart1, chart2 = st.columns(2)

        # --------------------------------
        # PIE CHART - CATEGORY WISE EXPENSES
        # --------------------------------

        with chart1:

            st.subheader("Expense by Category")

            if not expense_df.empty:

                category_data = expense_df.groupby(
                    "category"
                )["amount"].sum().reset_index()

                fig_pie = px.pie(
                    category_data,
                    names="category",
                    values="amount",
                    hole=0.4,
                    title="Where does your money go?",
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig_pie,
                    use_container_width=True
                )

            else:

                st.info("No expenses recorded yet.")

        # --------------------------------
        # BAR CHART - MONTHLY COMPARISON
        # --------------------------------

        with chart2:

            st.subheader("Monthly Income vs Expenses")

            analytics_df["month"] = (
                analytics_df["date"].dt.strftime("%Y-%m")
            )

            monthly_data = analytics_df.groupby(
                ["month", "type"]
            )["amount"].sum().unstack(fill_value=0)

            monthly_data = monthly_data.reindex(
                columns=["Income", "Expense"],
                fill_value=0
            )

            monthly_data = monthly_data.reset_index()

            fig_bar = px.bar(
                monthly_data,
                x="month",
                y=["Income", "Expense"],
                barmode="group",
                title="Monthly Financial Overview",
                labels={
                    "value": "Amount (₹)",
                    "month": "Month",
                    "variable": "Transaction Type"
                },
                color_discrete_map={
                    "Income": "#22C55E",
                    "Expense": "#EF4444"
                },
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True
            )

    else:

        st.info("No valid transaction dates available.")

else:

    st.info("Add transactions to see your expense analytics.")

st.divider()


# --------------------------------
# TRANSACTION MANAGEMENT
# --------------------------------

st.divider()

st.subheader("📋 Transaction Management")

df = get_transactions(user_id)

if not df.empty:

    # SEARCH TRANSACTIONS
    search_text = st.text_input(
        "🔍 Search by description or category",
        placeholder="Example: Food, Lunch, Books..."
    )

    # FILTER TRANSACTIONS
    filter_type = st.selectbox(
        "Filter by Transaction Type",
        ["All", "Income", "Expense"]
    )

    filtered_df = df.copy()

    if search_text:
        filtered_df = filtered_df[
            filtered_df["description"].str.contains(
                search_text,
                case=False,
                na=False
            ) |
            filtered_df["category"].str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    if filter_type != "All":
        filtered_df = filtered_df[
            filtered_df["type"] == filter_type
        ]

    # DISPLAY TRANSACTIONS
    st.subheader("Your Transactions")

    if not filtered_df.empty:

        display_df = filtered_df.copy()

        display_df["amount"] = display_df.apply(
            lambda row:
            f"↘ ₹{row['amount']:,.2f}"
            if row["type"] == "Income"
            else f"↙ ₹{row['amount']:,.2f}",
            axis=1
        )

        def color_amount(value):
            if str(value).startswith("↘"):
                return "color: #22C55E; font-weight: bold"
            return "color: #EF4444; font-weight: bold"

        styled_df = display_df.style.map(
            color_amount,
            subset=["amount"]
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No matching transactions found.")

    # EDIT TRANSACTION
    st.divider()

    st.subheader("✏️ Edit Transaction")

    transaction_ids = df["id"].tolist()

    selected_id = st.selectbox(
        "Select Transaction to Edit",
        transaction_ids,
        format_func=lambda x: (
            f"ID {x} - "
            f"{df.loc[df['id'] == x, 'description'].iloc[0]} "
            f"(₹{df.loc[df['id'] == x, 'amount'].iloc[0]:,.2f})"
        )
    )

    selected_row = df[df["id"] == selected_id].iloc[0]

    with st.form("edit_transaction_form"):

        edit_type = st.selectbox(
            "Transaction Type",
            ["Expense", "Income"],
            index=(
                0 if selected_row["type"] == "Expense" else 1
            )
        )

        edit_amount = st.number_input(
            "Amount (₹)",
            min_value=1.0,
            value=float(selected_row["amount"]),
            step=10.0
        )

        categories = [
            "Food",
            "Travel",
            "Shopping",
            "Education",
            "Entertainment",
            "Bills",
            "Salary",
            "Other"
        ]

        old_category = selected_row["category"]

        if old_category not in categories:
            categories.append(old_category)

        edit_category = st.selectbox(
            "Category",
            categories,
            index=categories.index(old_category)
        )

        edit_description = st.text_input(
            "Description",
            value=str(selected_row["description"] or "")
        )

        edit_date = st.date_input(
            "Date",
            value=pd.to_datetime(selected_row["date"]).date()
        )

        update_button = st.form_submit_button(
            "💾 Update Transaction"
        )

        if update_button:

            update_transaction(
                selected_id,
                edit_type,
                edit_amount,
                edit_category,
                edit_description,
                edit_date,
                user_id
            )

            st.success("Transaction updated successfully!")

            st.rerun()

    # DELETE TRANSACTION
    st.divider()

    st.subheader("🗑️ Delete Transaction")

    st.warning(
        "Deleting a transaction is permanent. "
        "Please check the selected transaction carefully."
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this transaction."
    )

    if st.button(
        "🗑️ Delete Selected Transaction",
        type="primary"
    ):

        if confirm_delete:

            delete_transaction(selected_id, user_id)

            st.success("Transaction deleted successfully!")

            st.rerun()

        else:

            st.error("Please confirm before deleting.")

else:

    st.info("No transactions available. Add your first transaction!")


# ==============================
# MONTHLY FINANCIAL COMPARISON
# ==============================

st.markdown("---")
st.header("📊 Monthly Financial Comparison")

comparison_df = get_transactions(user_id)

if not comparison_df.empty:

    comparison_df["date"] = pd.to_datetime(
        comparison_df["date"], errors="coerce"
    )
    comparison_df["amount"] = pd.to_numeric(
        comparison_df["amount"], errors="coerce"
    ).fillna(0)

    comparison_df = comparison_df.dropna(subset=["date"])
    comparison_df["month"] = comparison_df["date"].dt.to_period("M")
    comparison_df["type"] = (
        comparison_df["type"].astype(str).str.strip().str.lower()
    )

    current_month = pd.Timestamp.today().to_period("M")
    previous_month = current_month - 1

    def get_month_total(month, transaction_type):
        return comparison_df.loc[
            (comparison_df["month"] == month) &
            (comparison_df["type"] == transaction_type),
            "amount"
        ].sum()

    current_income = get_month_total(current_month, "income")
    current_expenses = get_month_total(current_month, "expense")
    previous_income = get_month_total(previous_month, "income")
    previous_expenses = get_month_total(previous_month, "expense")

    current_savings = current_income - current_expenses
    previous_savings = previous_income - previous_expenses

    def calculate_change(current, previous):
        if previous == 0:
            if current == 0:
                return "No change"
            return "No previous-month data"

        percentage = ((current - previous) / abs(previous)) * 100
        return f"{percentage:+.1f}% vs last month"

    st.caption(
        f"Comparing {previous_month.strftime('%B %Y')} "
        f"with {current_month.strftime('%B %Y')}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 This Month's Income",
            f"₹{current_income:,.2f}",
            calculate_change(current_income, previous_income)
        )

    with col2:
        st.metric(
            "💸 This Month's Expenses",
            f"₹{current_expenses:,.2f}",
            calculate_change(current_expenses, previous_expenses),
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "🏦 This Month's Savings",
            f"₹{current_savings:,.2f}",
            calculate_change(current_savings, previous_savings)
        )

    # Comparison chart
    chart_data = pd.DataFrame({
        "Month": [
            previous_month.strftime("%b %Y"),
            current_month.strftime("%b %Y")
        ],
        "Income": [previous_income, current_income],
        "Expenses": [previous_expenses, current_expenses]
    })

    chart_data = chart_data.melt(
        id_vars="Month",
        var_name="Transaction Type",
        value_name="Amount"
    )

    fig = px.bar(
        chart_data,
        x="Month",
        y="Amount",
        color="Transaction Type",
        barmode="group",
        color_discrete_map={
            "Income": "#22C55E",
            "Expenses": "#EF4444"
        },
        title="Income vs Expenses: Monthly Comparison",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Add some transactions to see your monthly comparison.")

# ==============================
# SMART SPENDING INSIGHTS
# ==============================

st.markdown("---")
st.header("🧠 Smart Spending Insights")

insight_df = get_transactions(user_id)

if not insight_df.empty:

    insight_df["amount"] = pd.to_numeric(
        insight_df["amount"], errors="coerce"
    ).fillna(0)

    expenses_df = insight_df[
        insight_df["type"].str.strip().str.lower() == "expense"
    ].copy()

    if not expenses_df.empty:

        total_spent = expenses_df["amount"].sum()
        average_expense = expenses_df["amount"].mean()

        largest_expense = expenses_df.loc[
            expenses_df["amount"].idxmax()
        ]

        category_spending = (
            expenses_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        top_category = category_spending.idxmax()
        top_category_amount = category_spending.max()

        top_percentage = (
            top_category_amount / total_spent * 100
            if total_spent > 0 else 0
        )

        # Key spending metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Money Spent",
                f"₹{total_spent:,.2f}"
            )

        with col2:
            st.metric(
                "Average Expense",
                f"₹{average_expense:,.2f}"
            )

        with col3:
            st.metric(
                "Highest Expense",
                f"₹{largest_expense['amount']:,.2f}"
            )

        st.markdown("### 🔍 Your Spending Analysis")

        st.write(
            f"Your highest spending category is **{top_category}**, "
            f"with ₹{top_category_amount:,.2f} spent."
        )

        st.write(
            f"This represents **{top_percentage:.1f}%** "
            "of your total expenses."
        )

        # Category spending chart
        category_chart = category_spending.reset_index()
        category_chart.columns = ["Category", "Amount"]

        fig_insights = px.bar(
            category_chart,
            x="Category",
            y="Amount",
            color="Amount",
            title="Your Spending by Category",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_insights,
            use_container_width=True
        )

        # Smart suggestions
        st.markdown("### 💡 Smart Saving Suggestions")

        if top_percentage >= 40:
            st.warning(
                f"You are spending a large portion of your money "
                f"on {top_category}. Try reducing this category's "
                "expenses gradually."
            )
        else:
            st.success(
                "Your spending is distributed across categories. "
                "Continue monitoring your expenses!"
            )

        st.info(
            f"Your largest recorded expense was "
            f"₹{largest_expense['amount']:,.2f} "
            f"for {largest_expense['category']} "
            f"({largest_expense['description']})."
        )

    else:
        st.info("Add some expense transactions to generate insights.")

else:
    st.info("Add transactions to unlock Smart Spending Insights.")
# --------------------------------
# EXPORT FINANCIAL REPORTS
# --------------------------------

st.divider()

st.subheader("📥 Download Financial Reports")

# Fetch all transactions
export_df = get_transactions(user_id)

if not export_df.empty:

    st.write(
        "Download your complete transaction history "
        "for backup and financial analysis."
    )

    # Create two download columns
    col1, col2 = st.columns(2)

    # --------------------------------
    # CSV DOWNLOAD
    # --------------------------------

    with col1:

        csv_data = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name="Expense_Tracker_Report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --------------------------------
    # EXCEL DOWNLOAD
    # --------------------------------

    with col2:

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            export_df.to_excel(
                writer,
                index=False,
                sheet_name="Transactions"
            )

        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="Expense_Tracker_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.success("Your financial reports are ready to download!")

else:

    st.info(
        "Add some transactions before downloading your reports."
    )


    


