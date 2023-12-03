import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.colors as mcolors
from pandas.io.formats.style import Styler
from plotly.subplots import make_subplots
import geopandas as gpd
import matplotlib
import altair as alt
import os, sys
import warnings
warnings.filterwarnings('ignore')
import folium
from streamlit_folium import folium_static
from folium.plugins import *
import geocoder
import branca.colormap as cm
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)



st.set_page_config(layout="wide")

##### LOGO ##########

st.markdown(
    f"""
    <div style="text-align: center">
        <img src="https://raw.githubusercontent.com/luisaporrasm/DVA_GaTech/main/logo_DVA.png" width="180">
    </div>
    """,
    unsafe_allow_html=True
)

##### FONT ###########
css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap');
    html, body, [class*="st-"] {{
        font-family: 'Roboto Condensed', sans-serif;
    }}
</style>
"""

# Inject CSS with markdown
st.markdown(css, unsafe_allow_html=True)

#### TITLE MIDDLE & DESCRIPTION #########

title_subtitle_css = """
<style>
.title-class {
    text-align: center;
    font-size: 80px;
    /* Additional styles if needed */
}

.subtitle-class {
    text-align: center;
    font-size: 30px; /* Subtitle font size */
    color: #E8F5E9; /* Subtitle text color */
    margin-top: 10px; /* Space between title and subtitle */
    margin-bottom: 20px; /* Space between subtitle and the rest of the content */
}

</style>
"""
st.markdown(title_subtitle_css, unsafe_allow_html=True)

st.markdown('<div class="title-class"><h1>Calgary Home Navigator: Dream, Decide, Dwell</h1></div>',
            unsafe_allow_html=True)

# Subtitle/Description
st.markdown('''
<div class="subtitle-class">
    <p><b>Dream Home or Smart Investment? Uncover Calgary's Best with our all-in-one affordability and market insight tool.</p>
    <p><b>Your journey to a savvy home choice starts here!<b></p>
</div>
''', unsafe_allow_html=True)

##### COLOR SLIDERS #######
# CSS in a Python multi-line string
slider_color_css = """
<style>
/* Target the slider track */
div[role="slider"] {
    background-color: #FF9100; /* This is the color of the slider track */
}

}
</style>
"""

# Use st.markdown to inject the defined CSS into the app
st.markdown(slider_color_css, unsafe_allow_html=True)

###### SUMMARY BOXES ##########

summary_box_css = """
<style>
.summary-box {
    background-color: #00695C;
    color: #ffffff; /*
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); /* Optional: Adds a shadow for a 3D effect */
    border-radius: 10px; /* Optional: Rounds the corners of the rectangle */
    padding: 20px; /* Adds space inside the rectangle between content and border */
    margin: 10px 0; /* Adds space outside the rectangle between it and other elements */
}
</style>
"""

# Inject the CSS into the app
st.markdown(summary_box_css, unsafe_allow_html=True)

####### FRAME #############

custom_css = """
<style>
.framed-col {
    border: 2px solid #009688;  /* border style*/
    border-radius: 5px;         /* Optional: for rounded corners */
    padding: 10px;              /* Optional: for some internal padding */
    margin: 5px;                /* Optional: for some space around the columns */
}
</style>
"""
# Inject the CSS into Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Modify the tabs to be rounded
st.markdown("""
<style>
    /* Target the container of the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; /* Space between tabs */
    }

    /* Style individual tabs */
    .stTabs [data-baseweb="tab"] {
        height: 25px; /* Increase height of the tab */
        border-radius: 10px; /* More pronounced rounded corners */
        padding-top: 20px; /* Increase padding at the top */
        padding-bottom: 20px; /* Increase padding at the bottom */
        padding-left: 10px; /* Optional: Add padding on the left */
        padding-right: 10px; /* Optional: Add padding on the right */
        font-size: 23px; /* Optional: Increase font size */
    }

    /* Style for the selected (active) tab */
    .stTabs [aria-selected="true"] {
        background-color: #FF9100; /* Change to your preferred color */
        color: #FFFFFF; /* Optional: Change text color if needed */
    }
</style>""", unsafe_allow_html=True)


# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Financial Fit Finder", "Buy vs. Rent Pathfinder", "Market Value Explorer", "Budget-Friendly Finds"])

# Content for Tab 1
with tab1:
    # st.write("This is the content of Tab 1")

    ######### FUNCTIONS CALCULATIONS ################################################################

    def calculate_stress_test_rate(base_rate, buffer, floor_rate):
        """
        Calculate the stress test rate for a mortgage.

        This function computes the stress test rate by adding a buffer to the base rate and ensuring that
        the result does not fall below a specified floor rate.

        Parameters:
        - base_rate (float): The base interest rate for the mortgage.
        - buffer (float): An additional percentage to add to the base rate as a buffer.
        - floor_rate (float): The minimum allowable rate after adding the buffer.

        Returns:
        - float: The higher value between the sum of the base rate and buffer, and the floor rate.
        """
        stress_test_rate = base_rate + buffer
        return max(stress_test_rate, floor_rate)


    def calculate_max_home_price(adjusted_monthly_income, annual_interest_rate, amortization_years, downpayment):
        """
        Calculate the estimated maximum home price based on financial parameters.

        This function estimates the maximum home price a person can afford based on their adjusted monthly income,
        the annual interest rate (considering a stress test rate), the length of the loan (amortization years),
        and the downpayment percentage.

        Parameters:
        - adjusted_monthly_income (float): The monthly income available for mortgage payments after deducting other expenses.
        - annual_interest_rate (float): The annual interest rate for the mortgage.
        - amortization_years (int): The total duration of the mortgage in years.
        - downpayment (float): The downpayment percentage of the total home price.

        Returns:
        - float: The estimated maximum price of a home that can be afforded.

        Note:
        The function includes a stress test by adding a 2% buffer to the annual interest rate. This buffer is included
        to assess the ability to maintain mortgage payments under potentially higher future interest rates.
        """

        # Apply stress test if required

        # Monthly interest rate. Assuming 2% buffer for the stress rate
        stress_test_rate = annual_interest_rate + 2
        monthly_interest_rate = stress_test_rate / 12 / 100  # converting percentage to decimal
        # Total number of payments
        total_payments = amortization_years * 12
        # Monthly payment for mortgage excluding taxes and insurance
        # estimated_taxes_insurance_per_month = adjusted_monthly_income * property_tax_and_insurance_rate / 12   # converting percentage to decimal
        # adjusted_monthly_income = adjusted_monthly_income - estimated_taxes_insurance_per_month
        # Maximum loan amount calculation
        max_loan_amount = (adjusted_monthly_income * (
                    1 - (1 + monthly_interest_rate) ** -total_payments)) / monthly_interest_rate
        # Estimated home price
        estimated_home_price = max_loan_amount / (1 - downpayment)  # (1-downpayment) is the loan amount

        return estimated_home_price


    def calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years):
        """
        Calculate the monthly mortgage payment for a given loan amount, interest rate, and loan term.

        This function computes the monthly mortgage payment incorporating a stress test by adding a 2% buffer
        to the annual interest rate. The function also calculates the total payment over the entire loan period and 
        the total interest paid over this period.

        Parameters:
        - loan_amount (float): The total amount of the loan or mortgage.
        - annual_interest_rate (float): The annual interest rate of the mortgage.
        - amortization_years (int): The total duration of the mortgage in years.

        Returns:
        - float: The monthly mortgage payment.

        Note:
        The function assumes a 2% buffer for the stress test on the interest rate. The total payment and total interest
        paid calculations are based on the entire duration of the mortgage.
        """
        # Assuming 2% buffer for the interest rate
        stress_test_rate = annual_interest_rate + 2
        monthly_interest_rate = stress_test_rate / 12 / 100
        total_payments = amortization_years * 12
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / (
                    (1 + monthly_interest_rate) ** total_payments - 1)

        # Calculate total payment over the entire period
        total_payment = monthly_payment * total_payments

        # Calculate total interest paid
        total_interest_paid = total_payment - loan_amount

        return monthly_payment


    def calculate_mortgage_insurance(loan_amount, ltv_ratio):
        """
    Calculate the mortgage insurance premium based on the loan amount and the loan-to-value (LTV) ratio.

    The insurance premium rate is determined by the LTV ratio. Different LTV ratio ranges are associated with
    different insurance premium rates.

    Parameters:
    - loan_amount (float): The total amount of the loan or mortgage.
    - ltv_ratio (float): The loan-to-value ratio, which is a financial term used by lenders to express the ratio of a loan
                          to the value of an asset purchased.

    Returns:
    - float: The calculated mortgage insurance premium.

    Note:
    The function applies different insurance premium rates based on the LTV ratio thresholds. It returns the calculated
    insurance premium amount based on the given loan amount and LTV ratio.
    """
        # Determine the insurance premium rate based on the LTV ratio
        if ltv_ratio <= 0.65:
            insurance_premium_rate = 0.0060  # 0.60%
        elif ltv_ratio <= 0.75:
            insurance_premium_rate = 0.0170  # 1.70%
        elif ltv_ratio <= 0.80:
            insurance_premium_rate = 0.0240  # 2.40%
        elif ltv_ratio <= 0.85:
            insurance_premium_rate = 0.0280  # 2.80%
        elif ltv_ratio <= 0.90:
            insurance_premium_rate = 0.0310  # 3.10%
        elif ltv_ratio <= 0.95:
            insurance_premium_rate = 0.0400  # 4.00%
        else:
            insurance_premium_rate = 0  #
        insurance_premium = loan_amount * insurance_premium_rate
        return insurance_premium


    def calculate_total_house_cost_with_interest(loan_amount, annual_interest_rate, amortization_years, downpayment):
        # Calculate the monthly mortgage payment
        monthly_payment = calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years)

        # Total number of payments
        total_payments = amortization_years * 12

        # Total amount paid over the loan period
        total_paid = monthly_payment * total_payments

        # Total cost of the house is the total paid plus the downpayment
        total_cost = total_paid + downpayment

        total_interest_paid = total_paid - loan_amount

        return total_cost, total_interest_paid


    def generate_data_interest(loan_amount, amortization_years, downpayment):
        interest_rates = [2, 3, 4, 5, 6, 7]
        data = []
        for rate in interest_rates:
            total_cost, total_interest_paid = calculate_total_house_cost_with_interest(loan_amount, rate,
                                                                                       amortization_years, downpayment)
            data.append([rate, total_cost, total_interest_paid])
        return data


    colors = ['#004D40', '#FFECB3', '#FFB74D']
    custom_cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)


    def style_table(df: pd.DataFrame) -> Styler:
        return df.style.format({
            'Total Cost': '${:,.0f}',
            'Total Interest Paid': '${:,.0f}'
        }) \
            .background_gradient(cmap=custom_cmap, subset=['Total Interest Paid']) \
            .background_gradient(cmap=custom_cmap, subset=['Total Cost']) \
            .set_properties(**{'text-align': 'center',
                               'width': '150px'}) \
            .set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ])


    # Initialize variables that need to be accessed in both columns

    monthly_mortgage_payment = None
    stress_test_rate = None
    total_debt_payments = None
    insurance_table = []
    max_price = None
    downpayments_percentages = [0.0501, 0.10, 0.15, 0.20]

    ########################## MORTGAGE CALCULATOR ###############################

    col1, col2, col3 = st.columns([1.5, 1.8, 1.5])  # Adjust the ratio as needed

    # col1,col2, col3 = st.columns(3)

    with col1.container():
        # st.markdown('<div class="framed-col">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #FFFDE7;">House Affordability Calculator</h2>', unsafe_allow_html=True)

        # Welcome message for the 'House Affordability Calculator' tab
        st.markdown(
            "Welcome to the 'House Affordability Calculator' - your personalized tool to determine the maximum house price you can afford based on your income, expenses, and mortgage details.")

        # Add an empty line (space) after the text
        st.write(" ")

        ### INCLUDE STRESS TEST  #####
        #### ADD THE INSURANCE IF DOWNPAYMENT IS LESS THAN 20%

        # User Inputs
        gross_income = st.number_input('Yearly Gross Income', min_value=0.0, value=100000.0, step=1000.0, format='%.2f',
                                       help='Enter your total yearly income before taxes')
        affordability_level = st.select_slider(
            'Affordability Level',
            options=([round(i * 0.1, 2) for i in range(0, 10)]),
            value=0.30,
            label_visibility="visible",
            help='Select how much of your disposable income is allocated to mortgage payments and monthly debt payments')
        annual_interest_rate = st.number_input('Annual Interest Rate (%)', min_value=0.0, value=4.0, step=0.1)
        amortization_years = st.number_input('Loan Term in Years', min_value=5, value=25, step=1,
                                             help='Amortization is the total time it takes to pay off your mortgage')
        downpayment = st.select_slider(
            'Down Payment',
            options=([round(i * 0.1, 2) for i in range(0, 9)]),
            value=0.20,
            label_visibility="visible",
            help='Down payment is a payment representing a fraction of the price of the property. In Canada, you can put as little as 5% down')

        ####### STRESS TEST ############################
        # New inputs for stress test and insurance calculation

        ############# OTHER DEBTS #######################
        # Checkbox to include debts
        include_debts = st.checkbox('Include Other Expenses (Debts)', False)

        # Conditional inputs for debts
        if include_debts:
            car_payment = st.number_input('Monthly Car Payment', min_value=0.0, value=0.0, step=50.0,
                                          help='Add up car loans or leases')
            credit_card_payment = st.number_input('Monthly Credit Card Payment', min_value=0.0, value=0.0, step=50.0,
                                                  help='Add up all monthly credit card payments')
            other_loans_payment = st.number_input('Monthly Other Loans Payment', min_value=0.0, value=0.0, step=50.0,
                                                  help='Add up all other personal loans or line of credit payments')
        else:
            car_payment = 0.0
            credit_card_payment = 0.0
            other_loans_payment = 0.0

        total_debt_payments = car_payment + credit_card_payment + other_loans_payment if include_debts else 0.0

        if st.button('Calculate Maximum House Price'):
            stress_test_rate = annual_interest_rate + 2
            monthly_gross_income = gross_income / 12
            monthly_available_income_house = monthly_gross_income - total_debt_payments
            adjusted_monthly_income = monthly_available_income_house * affordability_level
            max_price = calculate_max_home_price(adjusted_monthly_income, annual_interest_rate, amortization_years,
                                                 downpayment)

            st.session_state["estimated_home_price"] = max_price
            # st.success(f"The estimated maximum house price you can afford is: ${st.session_state.max_price:,.2f}")

            # Calculate loan amount
            loan_amount = max_price * (1 - downpayment)

            # Calculate LTV Ratio
            ltv_ratio = loan_amount / max_price

            # Monthly Mortgage Payment
            monthly_mortgage_payment = calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years)

            # insurance premium
            downpayment_amount = max_price * downpayment
            loan_amount = max_price - downpayment_amount
            ltv_ratio = loan_amount / max_price
            insurance_premium_property = calculate_mortgage_insurance(loan_amount, ltv_ratio)

            total_payments = amortization_years * 12
            monthly_insurance_premium_property = insurance_premium_property / total_payments

            # propery taxes: municipal and provincial
            monthly_property_tax_bill = ((max_price * 0.0043319) + (max_price * 0.0022399)) / 12

            # Mortgage Insurance Calculation for different downpayments
            downpayments_percentages = [0.0501, 0.10, 0.15, 0.20]

        # st.markdown('</div>', unsafe_allow_html=True)

    if monthly_mortgage_payment is not None:
        with col2.container():

            # st.markdown('<div class="framed-col">', unsafe_allow_html=True)

            # Creating the HTML content string with dynamic values
            if 'monthly_mortgage_payment' in locals():
                summary_html = f"""
                <div class="summary-box">
                    <h3>The estimated maximum house price you can afford is: $ {max_price:,.0f}</h3>
                    <p>Monthly Mortgage Payment: $ {monthly_mortgage_payment:,.0f}</p>
                    <p>Stress Test Rate (%): {stress_test_rate: .2f}</p>
                    <p>Monthly total Debt Payments: $ {total_debt_payments:,.0f}</p>
                    <p><br><b>Additional costs:</b><p>
                    <p> 2023 Monthly total property taxes (municipal and provincial): $ {monthly_property_tax_bill:,.0f} </p>
                    <p> 2023 Monthly Mortgage Insurance: $ {monthly_insurance_premium_property:,.0f} </p>
                </div>
                """

                # Display the HTML content with the custom styles applied
                st.markdown(summary_html, unsafe_allow_html=True)

            data = generate_data_interest(loan_amount, amortization_years, downpayment)
            df = pd.DataFrame(data, columns=['Interest Rate (%)', 'Total Cost', 'Total Interest Paid'])
            styled_df = style_table(df)
            st.write("**How much do you actually pay in interest?**")
            # Display the styled DataFrame
            # st.write(styled_df, unsafe_allow_html=True)
            st.table(styled_df)  # Or st.table(df) for a static table
            # st.markdown('</div>', unsafe_allow_html=True)

        # st.markdown('</div>', unsafe_allow_html=True)

        with col3.container():

            # st.markdown('<div class="framed-col">', unsafe_allow_html=True)

            # Define the color palette

            # Expenses data
            expenses = {"Mortgage": monthly_mortgage_payment, "Property Taxes": monthly_property_tax_bill,
                        "Mortgage Insurance": monthly_insurance_premium_property}

            # Define color palette
            color_palette = ['#00695C', '#FFECB3', '#FFB74D']

            # Expenses data
            expenses = {
                "Mortgage": monthly_mortgage_payment,
                "Property Taxes": monthly_property_tax_bill,
                "Mortgage Insurance": monthly_insurance_premium_property
            }

            # Data preparation
            df = pd.DataFrame(expenses.items(), columns=['Category', 'Amount'])

            # Creating the pie chart
            fig = go.Figure(data=[go.Pie(
                labels=df['Category'],
                values=df['Amount'],
                marker_colors=color_palette,
                textinfo='label+percent',  # Shows the label and the percentage
                hole=0.3  # You can adjust the size of the hole in the middle
            )])

            # Customizing the layout
            fig.update_layout(
                title={
                    'text': 'Monthly Expenses Breakdown',
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                legend=dict(
                    x=0.85,
                    y=1.15,
                    xanchor='center',
                    yanchor='top'
                ),
                width=450,
                height=450,
                showlegend=True
            )

            # Display the plot in Streamlit
            st.plotly_chart(fig)

# Content for Tab 2
with tab2:
    # st.write("This is the content of Tab 2")


    def set_bg_color():
        st.markdown(
            f"""
            <style>
            .reportview-container {{
                background-color: #ADD8E6;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


    # Defining a function to calculate the liquid net worth over time (Buying Scenario)
    def calculate_buying_liquid_net_worth(purchase_price, down_payment_percent, mortgage_interest_rate,
                                          amortization_period, home_appreciation_rate, property_tax_percent,
                                          initial_annual_maintenance, monthly_utilities, monthly_insurance,
                                          monthly_condo_fees,
                                          other_monthly_payments, sale_transaction_costs_percent, lump_sum_fee,
                                          general_inflation_rate):
        """
        Calculate the liquid net worth over time for a home purchase scenario.

        This function computes the year-over-year liquid net worth of buying a home, considering various expenses,
        mortgage payments, property appreciation, and other factors.

        Args:
            purchase_price (float): The purchase price of the home.
            down_payment_percent (float): The percentage of the purchase price paid as down payment.
            mortgage_interest_rate (float): The annual mortgage interest rate.
            amortization_period (int): The total number of years for mortgage repayment.
            home_appreciation_rate (float): The annual rate at which the home value appreciates.
            property_tax_percent (float): The annual property tax rate as a percentage of the home value.
            initial_annual_maintenance (float): The initial annual maintenance cost for the home.
            monthly_utilities (float): The monthly cost of utilities.
            monthly_insurance (float): The monthly cost of home insurance.
            monthly_condo_fees (float): The monthly condo fees, if applicable.
            other_monthly_payments (float): Any other monthly payments associated with the home.
            sale_transaction_costs_percent (float): The percentage of the home value to be paid as transaction costs when selling.
            lump_sum_fee (float): Lump sum fee added to the mortgage balance if down payment is less than 20%.
            general_inflation_rate (float): The general annual inflation rate.

        Returns:
            dict: A dictionary containing the liquid net worth calculations for each year of the amortization period.
            float: The initial down payment amount.
        """

        down_payment = purchase_price * (down_payment_percent / 100)
        initial_loan_amount = purchase_price - down_payment

        # Adding lump sum fee to the mortgage balance if down payment is less than 20%
        loan_amount = initial_loan_amount + lump_sum_fee if down_payment_percent < 20 else initial_loan_amount

        # Converting annual interest rate to monthly interest rate
        semi_annual_rate = mortgage_interest_rate / 2 / 100
        annual_effective_rate = (1 + semi_annual_rate) ** 2 - 1
        monthly_interest_rate = (1 + annual_effective_rate) ** (1 / 12) - 1
        total_payments = amortization_period * 12

        # Calculating monthly mortgage payment
        if mortgage_interest_rate == 0:
            monthly_payment = loan_amount / total_payments
        else:
            monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments)

        buying_liquid_net_worth_over_time = {}
        current_mortgage_balance = loan_amount

        for year in range(amortization_period + 1):
            # Calculating home value
            current_home_value = purchase_price * (1 + home_appreciation_rate / 100) ** year

            # Resetting interest and principal sums for the year
            annual_interest_sum = 0
            annual_principal_sum = 0

            for month in range(1, 13):
                if year > 0 and current_mortgage_balance > 0:
                    monthly_interest = current_mortgage_balance * monthly_interest_rate
                    monthly_principal = min(monthly_payment - monthly_interest, current_mortgage_balance)
                    current_mortgage_balance -= monthly_principal
                    annual_interest_sum += monthly_interest
                    annual_principal_sum += monthly_principal

            # Calculating annual expenses
            annual_property_tax = current_home_value * (property_tax_percent / 100) if year > 0 else 0
            annual_maintenance = initial_annual_maintenance * (
                        1 + general_inflation_rate / 100) ** year if year > 0 else 0
            annual_utilities = monthly_utilities * 12 if year > 0 else 0
            annual_insurance = monthly_insurance * 12 if year > 0 else 0
            annual_condo_fees = monthly_condo_fees * 12 if year > 0 else 0
            annual_other = other_monthly_payments * 12 if year > 0 else 0
            annual_housing_expense = monthly_payment * 12 + annual_property_tax + annual_maintenance + annual_utilities + annual_insurance + annual_condo_fees + annual_other

            # Calculating home equity and selling costs
            home_equity_pre_selling = current_home_value - current_mortgage_balance
            selling_costs = current_home_value * (sale_transaction_costs_percent / 100)
            home_equity_post_selling = home_equity_pre_selling - selling_costs

            # Storing results in the dictionary
            buying_liquid_net_worth_over_time[year] = {
                "Home Value": current_home_value,
                "Mortgage Balance": current_mortgage_balance,
                "Home Equity Pre-Selling": home_equity_pre_selling,
                "Selling Costs": selling_costs,
                "Home Equity Post-Selling": home_equity_post_selling,
                "Annual Housing Expense": annual_housing_expense,
                "Implied Monthly Housing Expense": annual_housing_expense / 12,
                "Liquid Net Worth": home_equity_post_selling,
                "Interest Payment": annual_interest_sum,
                "Principal Payment": annual_principal_sum,
                "Annual Property Tax": annual_property_tax,
                "Annual Maintenance": annual_maintenance,
                "Annual Utilities": annual_utilities,
                "Annual Insurance": annual_insurance,
                "Annual Condo Fees": annual_condo_fees,
                "Annual Other": annual_other
            }

        return buying_liquid_net_worth_over_time, down_payment


    def calculate_rental_liquid_net_worth(home_purchase_costs, down_payment_amount, monthly_rent_payment,
                                          annual_rent_increase, monthly_utilities, monthly_renters_insurance,
                                          other_monthly_fees, annual_investment_return, buying_annual_housing_expenses):
        """
        Calculate the liquid net worth over time for a rental scenario.

        This function computes the year-over-year liquid net worth of renting a property, considering rent payments,
        utility costs, insurance, and investment returns on the money that would have been spent on buying a home.

        Args:
            home_purchase_costs (float): The upfront costs involved in purchasing a home.
            down_payment_amount (float): The down payment amount for a home purchase.
            monthly_rent_payment (float): The monthly rent payment for the rental property.
            annual_rent_increase (float): The annual percentage increase in rent.
            monthly_utilities (float): The monthly cost of utilities for the rental property.
            monthly_renters_insurance (float): The monthly cost of renters' insurance.
            other_monthly_fees (float): Any other monthly fees associated with renting.
            annual_investment_return (float): The annual return rate on investments.
            buying_annual_housing_expenses (list): List of annual housing expenses if buying a home.

        Returns:
            dict: A dictionary containing the liquid net worth calculations for each year of the comparison period.
        """

        # Initial Investment Portfolio
        implied_initial_investment_portfolio = home_purchase_costs + down_payment_amount
        eop_investment_portfolio = implied_initial_investment_portfolio

        rental_liquid_net_worth_over_time = {}
        annual_rent_payment = monthly_rent_payment * 12

        for year in range(len(buying_annual_housing_expenses)):
            # BOP Investment Portfolio is the EOP from the previous year
            bop_investment_portfolio = eop_investment_portfolio

            # Calculating Annual Housing Expense for Renting
            annual_housing_expense_renting = annual_rent_payment + (
                        monthly_utilities + monthly_renters_insurance + other_monthly_fees) * 12

            if year > 0:
                # Adjusting for rent increase from year 1 onwards
                annual_rent_payment *= (1 + annual_rent_increase / 100)
                # Incremental Cash Flows versus Buying
                incremental_cash_flows = max(0, -1 * annual_housing_expense_renting - (
                            -1 * buying_annual_housing_expenses[year]))
                # Investment Return
                investment_return = bop_investment_portfolio * (annual_investment_return / 100)
                # EOP Investment Portfolio Calculation
                eop_investment_portfolio = bop_investment_portfolio + incremental_cash_flows + investment_return
            else:
                # For year 0, there are no incremental cash flows or investment returns
                annual_housing_expense_renting = 0
                incremental_cash_flows = 0

            # Liquid Net Worth Calculation
            liquid_net_worth = eop_investment_portfolio

            rental_liquid_net_worth_over_time[year] = {
                "Annual Housing Expense Renting": annual_housing_expense_renting,
                "BOP Investment Portfolio": bop_investment_portfolio,
                "EOP Investment Portfolio": eop_investment_portfolio,
                "Incremental Cash Flow": incremental_cash_flows,
                "Liquid Net Worth": liquid_net_worth,
                "Annual Rent Payment": annual_rent_payment,
                "Annual Utilities": monthly_utilities * 12,
                "Annual Renters Insurance": monthly_renters_insurance * 12,
                "Other Annual Fees": other_monthly_fees * 12
            }

        return rental_liquid_net_worth_over_time


    # st.set_page_config(page_title="My App", layout='wide')

    def main():
        set_bg_color()
        st.markdown('<h2 style="color: #FFFDE7;">Buy vs. Rent Calculator</h2>', unsafe_allow_html=True)

        st.markdown(
            "Make an informed decision between buying and renting with our 'Buy vs. Rent Calculator'. Input your financial details to compare the long-term impact on your net worth, and see a clear visualization of potential financial outcomes over time.")

        # Adding an empty line (space) after the text
        st.write(" ")

        # Initializing session_state variables if they are not already defined
        if 'general_inflation_rate' not in st.session_state:
            st.session_state.general_inflation_rate = 0.0

        if 'home_purchase_price' not in st.session_state:
            st.session_state.home_purchase_price = 0.0

        if 'down_payment_amount' not in st.session_state:
            st.session_state.down_payment_amount = 0.0

        if 'home_purchase_costs' not in st.session_state:
            st.session_state.home_purchase_costs = 0.0

        # Custom CSS to add padding on the left
        st.markdown("""
            <style>
            .reportview-container .main .block-container {
                padding-left: 5rem;  /* Adjust the value as needed */
            }
            /* Decrease the vertical spacing */
            .row-widget.stRadio > div {
                margin: 0;  /* Adjust vertical spacing for radio buttons */
            }
            .block-container > div {
                margin-bottom: -20px;  /* Adjust vertical spacing for other widgets */
            }
            /* Position the question mark icon */
            .tooltip-icon {
                display: inline-block;
                position: relative;
                top: -26px;  /* Adjust vertical position */
                left: 5px;   /* Adjust horizontal position */
            }
            </style>
            """, unsafe_allow_html=True)

        # Defining columns
        buffer, col2, col3 = st.columns([1.5, 1.5, 4])

        # Initializing the variables
        years = []
        net_worth_values = []
        home_values = []
        mortgage_balances = []

        with buffer:
            with st.form("buying_inputs"):
                st.markdown("### Buying Scenario Assumptions")  # Larger header
                # st.header("Buying Scenario Assumptions")

                # def info_icon(tooltip_text):
                #     # Styling the question mark to be white, bold, and to the right top of the input box
                #     html_str = f"""
                #     <span class="tooltip-icon" title="{tooltip_text}" style="font-size: 20px; font-weight: bold; color: white; cursor: pointer;">?</span>
                #     """
                #     return components.html(html_str, height=30)

                # Home Purchase Price
                st.session_state.home_purchase_price = st.number_input("Home Purchase Price ($)",
                                                                       value=st.session_state.home_purchase_price,
                                                                       min_value=0.0,
                                                                       help="Enter the purchase price of the home. This is the total amount you will pay for the property.")
                # info_icon("Enter the purchase price of the home. This is the total amount you will pay for the property.")

                # Down Payment Percent
                down_payment_percent = st.number_input("Down Payment as a % of Home Value", min_value=0.0,
                                                       max_value=100.0,
                                                       value=5.0,
                                                       help="Enter the percentage of the home's value that you will pay as a down payment.")

                # Determining Mortgage Insurance Need and Lump Sum Fee
                if down_payment_percent < 20:
                    mortgage_insurance_needed = "Yes"
                    lump_sum_fee = st.number_input("Lump Sum Fee Added to Mortgage Balance ($)", value=2000.0,
                                                   help="Enter the lump sum fee that will be added to the mortgage balance. This is the fee charged by the lender for mortgage insurance. If down payment is less than 20%, mortgage insurance is required.")
                else:
                    mortgage_insurance_needed = "No"
                    lump_sum_fee = 0.0  # Set lump sum fee to zero if down payment is 20% or more

                # Display mortgage insurance requirement (optional)
                st.write(f"Mortgage Insurance Needed: {mortgage_insurance_needed}")

                # Annual Home Value Appreciation
                annual_home_appreciation = st.number_input("Annual Home Value Appreciation (%)", min_value=0.0, value=4.0,
                                                           help="Enter the expected annual rate at which your home's value will increase.")
                # info_icon("Enter the expected annual rate at which your home's value will increase.")

                # Average Mortgage Interest Rate
                mortgage_interest_rate = st.number_input("Average Mortgage Interest Rate (%)", min_value=0.0, value=5.0,
                                                         help="Enter the average interest rate for your mortgage over its entire term.")
                # info_icon("Enter the average interest rate for your mortgage over its entire term.")

                # Mortgage Amortization Period
                mortgage_amortization = st.number_input("Mortgage Amortization Period (years)", min_value=1, value=25,
                                                        help="Enter the number of years over which the mortgage will be fully repaid.")
                # info_icon("Enter the number of years over which the mortgage will be fully repaid.")

                # Annual Property Tax Percent
                annual_property_tax_percent = st.number_input("Annual Property Tax as a % of Home Value (%)",
                                                              min_value=0.0,
                                                              value=1.0,
                                                              help="Enter the annual property tax rate as a percentage of your home's value.")
                # info_icon("Enter the annual property tax rate as a percentage of your home's value.")

                # Annual Home Maintenance
                initial_annual_maintenance = st.number_input("Annual Home Maintenance ($ per year)", min_value=0.0, value=2000.0,
                                                             help="Enter the estimated annual cost for home repairs, upgrades, and regular maintenance.")
                # info_icon("Enter the estimated annual cost for home repairs, upgrades, and regular maintenance.")

                # Monthly Utilities Payment
                monthly_utilities = st.number_input("Monthly Utilities Payment ($ per month)", min_value=0.0, value=300.0,
                                                    help="Enter your estimated monthly cost for utilities like heat, electricity, and water.")
                # info_icon("Enter your estimated monthly cost for utilities like heat, electricity, and water.")

                # Monthly Homeowner's Insurance Payment
                monthly_insurance = st.number_input("Monthly Homeowner's Insurance Payment ($ per month)",
                                                    min_value=0.0,
                                                    value=100.0,
                                                    help="Enter the monthly cost of your homeowner's insurance.")
                # info_icon("Enter the monthly cost of your homeowner's insurance.")

                # Monthly Condo Fee Payment
                monthly_condo_fees = st.number_input("Monthly Condo Fee Payment ($ per month)", value=0.0,
                                                     help="If applicable, enter your monthly condo fees. Default is zero.")
                # info_icon("If applicable, enter your monthly condo fees. Default is zero.")

                # Other Monthly Payments
                other_monthly_payments = st.number_input("Other Monthly Payments ($ per month)", value=0.0,
                                                         help="Enter any other monthly payments related to your home.")
                # info_icon("Enter any other monthly payments related to your home.")

                # Home Purchase Transaction Costs
                st.session_state.home_purchase_costs = st.number_input("Home Purchase Transaction Costs ($)",
                                                                       value=st.session_state.home_purchase_costs,
                                                                       min_value=0.0,
                                                                       help="Enter one-time costs paid during the home purchase like land transfer tax, legal fees, and home inspection.")
                # info_icon("Enter one-time costs paid during the home purchase like land transfer tax, legal fees, and home inspection.")

                # Home Sale Transaction Costs Percent
                home_sale_costs_percent = st.number_input("Home Sale Transaction Costs as a % of Home Value (%)",
                                                          min_value=0.0,
                                                          value=4.0,
                                                          help="Enter the percentage of the home's value that will be paid as transaction costs when selling the home.")
                # info_icon("Enter the percentage of the home's value that will be paid as transaction costs when selling the home.")

                submit_button = st.form_submit_button(label='Calculate')

                if submit_button:
                    # Performing calculation
                    liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                        st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                        mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                        initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                        other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                        st.session_state.general_inflation_rate)

                    # Storing the calculated down payment amount in session_state
                    st.session_state.down_payment_amount = down_payment_amount
                    st.session_state.liquid_net_worth = liquid_net_worth

                    # # Displaying the results
                    # st.write("Buying Liquid Net Worth Over Time:")
                    # for year, data in liquid_net_worth.items():
                    #     st.write(f"Year {year}:")
                    #     st.write(f"Home Value: ${data['Home Value']:,.2f}")
                    #     st.write(f"Mortgage Balance: ${data['Mortgage Balance']:,.2f}")
                    #     st.write(f"Home Equity (Pre-Selling): ${data['Home Equity Pre-Selling']:,.2f}")
                    #     st.write(f"Selling Costs: ${data['Selling Costs']:,.2f}")
                    #     st.write(f"Home Equity (Post-Selling): ${data['Home Equity Post-Selling']:,.2f}")
                    #     st.write(f"Annual Housing Expense: ${data['Annual Housing Expense']:,.2f}")
                    #     st.write(f"Monthly Housing Expense: ${data['Implied Monthly Housing Expense']:,.2f}")
                    #     st.write(f"Liquid Net Worth: ${data['Liquid Net Worth']:,.2f}")
                    #     st.write(f"Interest Payment: ${data['Interest Payment']:,.2f}")
                    #     st.write(f"Principal Payment: ${data['Principal Payment']:,.2f}")
                    #     st.write("---")  # Add a separator for readability

                    # Preparing data for plotting
                    years = list(liquid_net_worth.keys())
                    net_worth_values = [data['Liquid Net Worth'] for data in liquid_net_worth.values()]
                    home_values = [data['Home Value'] for data in liquid_net_worth.values()]
                    mortgage_balances = [data['Mortgage Balance'] for data in liquid_net_worth.values()]
                    interest_payments = [data['Interest Payment'] for data in liquid_net_worth.values()]
                    principal_payments = [data['Principal Payment'] for data in liquid_net_worth.values()]

                    interest_payments_cum = np.cumsum(interest_payments)
                    principal_payments_cum = np.cumsum(principal_payments)

        # Other columns can be used for additional content if needed
        with col2:
            st.markdown("### Rental Scenario Assumptions")
            # st.header("Rental Scenario Assumptions")
            st.write("\n")

            monthly_rent_payment = st.number_input("Monthly Rent Payment ($ per month)", min_value=0.0, value=2000.0,
                                                   help="Enter your monthly rent payment.")
            annual_rent_increase = st.number_input("Annual Rent Increase (%)", min_value=0.0, value=2.0,
                                                   help="Enter the expected annual rate at which your rent will increase.")
            monthly_utilities_rental = st.number_input("Monthly Utilities Payment (Rental) ($ per month)",
                                                       min_value=0.0, value=150.0,
                                                       help="Enter your estimated monthly cost for utilities like heat, electricity, and water.")
            monthly_renters_insurance = st.number_input("Monthly Renter's Insurance Payment ($ per month)",
                                                        min_value=0.0, value=50.0,
                                                        help="Enter the monthly cost of your renter's insurance.")
            other_monthly_payments_rental = st.number_input("Other Monthly Payments (Rental) ($ per month)",
                                                            min_value=0.0,
                                                            help="Enter any other monthly payments related to your rental.")
            annual_investment_return = st.number_input("Annual After-Tax Investment Return (Nominal) (%)",
                                                       min_value=0.0,
                                                       help="Enter the expected annual after-tax investment return on your investment portfolio.")
            st.session_state.general_inflation_rate = st.number_input("General Inflation Rate (%)",
                                                                      value=st.session_state.general_inflation_rate,
                                                                      min_value=0.0,
                                                                      help="Enter the expected annual inflation rate.")


            # Rental Scenario Calculations
            if submit_button:
                # Extracting the annual housing expense from the buying results for comparison
                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                # st.write("General Inflation Rate: ", st.session_state.general_inflation_rate)
                # st.write("Home Purchase Price: ", st.session_state.home_purchase_price)
                # st.write("Down Payment Amount: ", st.session_state.down_payment_amount)
                # st.write("Home Purchase Costs: ", st.session_state.home_purchase_costs)

                # Calculating the Rental Liquid Net Worth
                rental_results = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                   st.session_state.down_payment_amount,
                                                                   monthly_rent_payment,
                                                                   annual_rent_increase, monthly_utilities_rental,
                                                                   monthly_renters_insurance,
                                                                   other_monthly_payments_rental,
                                                                   annual_investment_return,
                                                                   buying_annual_housing_expenses)

                # # Displaying the results
                # st.write("Rental Liquid Net Worth Over Time:")
                # for year, data in rental_results.items():
                #     st.write(f"Year {year}:")
                #     st.write(f"Annual Housing Expense (Renting): ${data['Annual Housing Expense Renting']:,.2f}")
                #     st.write(f"BOP Investment Portfolio: ${data['BOP Investment Portfolio']:,.2f}")
                #     st.write(f"EOP Investment Portfolio: ${data['EOP Investment Portfolio']:,.2f}")
                #     st.write(f"Incremental Cash Flow: ${data['Incremental Cash Flow']:,.2f}")
                #     st.write(f"Liquid Net Worth: ${data['Liquid Net Worth']:,.2f}")
                #     st.write("---")  # Add a separator for readability

        with col3:
            # st.write("This is in column 3")

            if submit_button:

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                # crossover_month = None
                # crossover_time = None

                # # Looping through the years to find the crossover interval
                # for year in range(mortgage_amortization - 1):
                #     buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                #     buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                #     rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                #     rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                #     if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                #         # Interpolate within this year range
                #         for month in range(1, 13):  # Check each month
                #             fraction_of_year = month / 12.0
                #             interpolated_buying = buying_current_year + (buying_next_year - buying_current_year) * fraction_of_year
                #             interpolated_rental = rental_current_year + (rental_next_year - rental_current_year) * fraction_of_year

                #             if interpolated_buying >= interpolated_rental:
                #                 crossover_month = month
                #                 crossover_time = year + fraction_of_year
                #                 break

                #         if crossover_month is not None:
                #             break

                # if crossover_time is not None:
                #     st.markdown(f"""
                #     <style>
                #         .highlight {{
                #             font-size: 20px;
                #             color: red;
                #         }}
                #     </style>
                #     <p>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                #     """, unsafe_allow_html=True)

                # # if crossover_time is not None:
                # #     st.write(f"Initially, renting is the better option. After ~{crossover_time:.2f} years, buying becomes the better option.")
                # else:
                #     st.write("No crossover detected within the amortization period.")

                # Extract Rental Liquid Net Worth values
                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_results.values()]

                # Initialize a list to store the differences
                net_worth_differences = []

                # Calculate the difference for each year
                for year in years:
                    buying_net_worth = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_net_worth = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    difference = - buying_net_worth + rental_net_worth
                    net_worth_differences.append(difference)

                    # Optionally, display the difference per year
                    # st.write(f"Year {year} Difference: ${difference:,.2f}")

            st.markdown(f"""
            <style>
                .custom-text2 {{
                    font-size: 25px;  /* Font size for the entire paragraph */
                    color: yellow;
                    margin-bottom: -10px;  /* Reduce bottom margin */
                }}
                .selectbox-label {{
                    margin-top: -10px;  /* Reduce top margin */
                }}
            </style>
            <p class='custom-text2'>Select a Plot from the dropdown below: </p>
            """, unsafe_allow_html=True)

            plot_option = st.selectbox(
                '',
                ('Buying vs Renting Net Worth', 'Home Value and Mortgage Balance', 'Annual Housing Expense Comparison',
                 'Annual Housing Expense - Buying', 'Annual Housing Expense - Renting', 'Tables - Calculated Results')
            )

            st.write('\n')

            # Buying vs Renting Net Worth
            if plot_option == 'Buying vs Renting Net Worth':

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  buying_liquid_net_worth.values()]

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolating within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                # Creating Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()]
                })

                # Creating Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()]
                })

                # Preparing data for plotting
                years = list(buying_liquid_net_worth.keys())
                net_worth_values = [data['Liquid Net Worth'] for data in buying_liquid_net_worth.values()]
                home_values = [data['Home Value'] for data in buying_liquid_net_worth.values()]
                mortgage_balances = [data['Mortgage Balance'] for data in buying_liquid_net_worth.values()]
                interest_payments = [data['Interest Payment'] for data in buying_liquid_net_worth.values()]
                principal_payments = [data['Principal Payment'] for data in buying_liquid_net_worth.values()]

                interest_payments_cum = np.cumsum(interest_payments)
                principal_payments_cum = np.cumsum(principal_payments)

                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_liquid_net_worth.values()]

                # Extracting Rental Liquid Net Worth values
                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_liquid_net_worth.values()]

                # Initializing a list to store the differences
                net_worth_differences = []

                # Calculating the difference for each year
                for year in years:
                    buying_net_worth = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_net_worth = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    difference = - buying_net_worth + rental_net_worth
                    net_worth_differences.append(difference)

                    # ['#004D40', '#FFECB3', '#FFB74D']

                if years:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=years, y=net_worth_values, mode='lines+markers', name='Buy',
                                             marker_color='#FFD740'))
                    fig.add_trace(go.Scatter(x=years, y=rental_net_worth_values, mode='lines+markers', name='Rent',
                                             marker_color='#FF6F00'))
                    # fig.add_trace(go.Scatter(x=years, y=home_values, mode='lines+markers', name='Home Value'))
                    # fig.add_trace(go.Scatter(x=years, y=mortgage_balances, mode='lines+markers', name='Mortgage Balance'))
                    fig.add_trace(go.Scatter(x=years, y=net_worth_differences, mode='lines+markers',
                                             name='Difference in Net Worth', marker_color='#00BFA5'))

                    fig.update_layout(
                        title='Liquid Net Worth Over Time',
                        xaxis_title='Year',
                        yaxis_title='Amount ($)',
                        width=800,  # Width of the figure in pixels
                        height=600  # Height of the figure in pixels
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # Home Value and Mortgage Balance
            elif plot_option == 'Home Value and Mortgage Balance':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                years = list(buying_liquid_net_worth.keys())
                net_worth_values = [data['Liquid Net Worth'] for data in buying_liquid_net_worth.values()]
                home_values = [data['Home Value'] for data in buying_liquid_net_worth.values()]
                mortgage_balances = [data['Mortgage Balance'] for data in buying_liquid_net_worth.values()]
                interest_payments = [data['Interest Payment'] for data in buying_liquid_net_worth.values()]
                principal_payments = [data['Principal Payment'] for data in buying_liquid_net_worth.values()]

                interest_payments_cum = np.cumsum(interest_payments)
                principal_payments_cum = np.cumsum(principal_payments)

                if years:
                    fig = go.Figure()
                    # fig.add_trace(go.Scatter(x=years, y=net_worth_values, mode='lines+markers', name='Buy'))
                    fig.add_trace(go.Scatter(x=years, y=home_values, mode='lines+markers', name='Home Value'))
                    fig.add_trace(
                        go.Scatter(x=years, y=mortgage_balances, mode='lines+markers', name='Mortgage Balance'))
                    fig.add_trace(
                        go.Scatter(x=years, y=interest_payments_cum, mode='lines+markers', name='Interest Payments'))
                    fig.add_trace(
                        go.Scatter(x=years, y=principal_payments_cum, mode='lines+markers', name='Principal Payments'))

                    fig.update_layout(
                        title='Home Value and Mortgage Balance Over Time',
                        xaxis_title='Year',
                        yaxis_title='Amount ($)',
                        width=800,  # Width of the figure in pixels
                        height=600  # Height of the figure in pixels
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Annual Housing Expense Comparison
            elif plot_option == 'Annual Housing Expense Comparison':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                # Creating Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()]
                })

                # Creating Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()]
                })

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=buying_df['Year'],
                    y=buying_df['Annual Housing Expense'],
                    name='Buying',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=renting_df['Year'],
                    y=renting_df['Annual Housing Expense Renting'],
                    name='Renting',
                    marker_color='red'
                ))

                # Update layout
                fig.update_layout(
                    title='Comparison of Annual Housing Expenses: Buying vs Renting',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expense ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    barmode='group',
                    bargap=0.15,  # gap between bars of adjacent location coordinates
                    bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=800,  # Width of the figure in pixels
                    height=600  # Height of the figure in pixels
                )

                # Displaying the plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)

            elif plot_option == 'Annual Housing Expense - Buying':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolating within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Creating Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()],
                    "Annual Property Tax": [data["Annual Property Tax"] for data in buying_liquid_net_worth.values()],
                    "Annual Maintenance": [data["Annual Maintenance"] for data in buying_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in buying_liquid_net_worth.values()],
                    "Annual Insurance": [data["Annual Insurance"] for data in buying_liquid_net_worth.values()],
                    "Annual Condo Fees": [data["Annual Condo Fees"] for data in buying_liquid_net_worth.values()],
                    "Annual Other": [data["Annual Other"] for data in buying_liquid_net_worth.values()]
                })

                # Extracting data from the dataframes
                years = buying_df['Year']
                buying_mortgage_principal = buying_df['Principal Payment']
                buying_mortgage_interest = buying_df['Interest Payment']
                buying_property_taxes = buying_df['Annual Property Tax']
                buying_maintenance = buying_df['Annual Maintenance']
                buying_utilities = buying_df['Annual Utilities']
                buying_insurance = buying_df['Annual Insurance']
                buying_condo_fees = buying_df['Annual Condo Fees']
                buying_other = buying_df['Annual Other']

                # Buying scenario plot
                fig_buying = go.Figure(data=[
                    go.Bar(name='Mortgage Principal', x=years, y=buying_mortgage_principal),
                    go.Bar(name='Mortgage Interest', x=years, y=buying_mortgage_interest),
                    go.Bar(name='Property Taxes', x=years, y=buying_property_taxes),
                    go.Bar(name='Maintenance', x=years, y=buying_maintenance),
                    go.Bar(name='Utilities', x=years, y=buying_utilities),
                    go.Bar(name='Insurance', x=years, y=buying_insurance),
                    go.Bar(name='Condo Fees', x=years, y=buying_condo_fees),
                    go.Bar(name='Other', x=years, y=buying_other)
                ])

                # Changing the bar mode to stack
                fig_buying.update_layout(
                    barmode='stack',
                    title='Buying Annual Expenses Breakdown',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expenses ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=1.0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    # barmode='group',
                    # bargap=0.15,  # gap between bars of adjacent location coordinates
                    # bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=1100,  # Width of the figure in pixels
                    height=700  # Height of the figure in pixels
                )

                # Displaying the plots in Streamlit
                st.plotly_chart(fig_buying)


            elif plot_option == 'Annual Housing Expense - Renting':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolating within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Creating Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()],
                    "Annual Rent Payment": [data["Annual Rent Payment"] for data in rental_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in rental_liquid_net_worth.values()],
                    "Annual Renters Insurance": [data["Annual Renters Insurance"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Other Annual Fees": [data["Other Annual Fees"] for data in rental_liquid_net_worth.values()]
                })

                # Extracting data from the dataframes
                years = renting_df['Year']
                renting_rent = renting_df['Annual Rent Payment']
                renting_utilities = renting_df['Annual Utilities']
                renting_insurance = renting_df['Annual Renters Insurance']
                renting_other = renting_df['Other Annual Fees']

                # Renting scenario plot
                fig_renting = go.Figure(data=[
                    go.Bar(name='Rent', x=years, y=renting_rent),
                    go.Bar(name='Utilities', x=years, y=renting_utilities),
                    go.Bar(name='Insurance', x=years, y=renting_insurance),
                    go.Bar(name='Other Fees', x=years, y=renting_other)
                ])

                # Changing the bar mode to stack
                fig_renting.update_layout(
                    barmode='stack',
                    title='Renting Annual Expenses Breakdown',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expenses ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=1.0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    # barmode='group',
                    # bargap=0.15,  # gap between bars of adjacent location coordinates
                    # bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=1100,  # Width of the figure in pixels
                    height=700  # Height of the figure in pixels
                )

                # Displaying the plots in Streamlit
                st.plotly_chart(fig_renting)


            elif plot_option == 'Tables - Calculated Results':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Looping through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolating within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Creating Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()],
                    "Annual Property Tax": [data["Annual Property Tax"] for data in buying_liquid_net_worth.values()],
                    "Annual Maintenance": [data["Annual Maintenance"] for data in buying_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in buying_liquid_net_worth.values()],
                    "Annual Insurance": [data["Annual Insurance"] for data in buying_liquid_net_worth.values()],
                    "Annual Condo Fees": [data["Annual Condo Fees"] for data in buying_liquid_net_worth.values()],
                    "Annual Other": [data["Annual Other"] for data in buying_liquid_net_worth.values()]
                })

                # Creating Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()],
                    "Annual Rent Payment": [data["Annual Rent Payment"] for data in rental_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in rental_liquid_net_worth.values()],
                    "Annual Renters Insurance": [data["Annual Renters Insurance"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Other Annual Fees": [data["Other Annual Fees"] for data in rental_liquid_net_worth.values()]
                })

                # Creating and styling the DataFrame
                buying_heatmap_columns = ['Home Value', 'Mortgage Balance', 'Liquid Net Worth']
                renting_heatmap_columns = ['Liquid Net Worth']

                styled_buying_df = buying_df.style.background_gradient(cmap='coolwarm', subset=buying_heatmap_columns)
                styled_renting_df = renting_df.style.background_gradient(cmap='coolwarm',
                                                                         subset=renting_heatmap_columns)

                # Displaying styled DataFrame in Streamlit
                st.dataframe(styled_buying_df)
                st.dataframe(styled_renting_df)

        # with col4:
        #     st.write("This column is half the size of 2 and 3")


    if __name__ == "__main__":
        main()

# Content for Tab 3
with tab3:
    ####### CHANGE COLOR TAB ################

    # Define custom styles using CSS
    custom_css_tab3 = """
        <style>
            /* You can use .st-ck to target the multiselect widget container */
            .st-ck {
                background-color: #00695C; /* Dark background for better contrast */
            }
            /* Use .st-bq to target the multiselect widget options */
            .st-bq {
                color: #FFAB40; /* White text color for better contrast */
            }
        </style>
    """

    # Inject custom CSS with markdown
    st.markdown(custom_css_tab3, unsafe_allow_html=True)

    ######## CHANGE COLOR TEXT BOX SELECTION ###########

    # Custom CSS to inject via markdown
    custom_css = """
        <style>
            /* Target the multiselect widget's text */
            .Select-multi-value-wrapper .Select-value-label {
                color: ##F9FBE7;
            }
            /* You may also need to change the color of the placeholder text */
            .Select-placeholder {
                color: ##F9FBE7;
            }
        </style>
    """

    # Inject custom CSS with markdown
    st.markdown(custom_css, unsafe_allow_html=True)

    # Write custom CSS
    custom_css_text = """
        <style>
            /* Target the container of the selected options */
            .css-12jo7m5 {
                color: #000000; /* Change to desired text color, e.g., black */
            }

            /* Target the specific labels of the selected options */
            .css-tlfecz-indicatorContainer {
                color: #000000; /* Change to desired text color, e.g., black */
            }

            /* You may also need to adjust the color when hovering */
            .css-12jo7m5:hover {
                color: #000000; /* Change to desired text color, e.g., black */
            }
        </style>
    """

    # Inject the custom CSS into the Streamlit app
    st.markdown(custom_css_text, unsafe_allow_html=True)

    st.markdown('<h2 style="color: #FFFDE7;">Community Valuation Trends</h2>', unsafe_allow_html=True)

    st.markdown(
        "Zoom into the real estate landscape with 'Community Valuation Trends', where you can compare the average assessed property values across communities over time. Dive in, select various neighborhoods, and witness the average price evolution on an intuitive map.")
    st.write(" ")

    # import data
    @st.cache_data
    def load_data():
        df = pd.read_pickle('Grouped_Data_ALL-Years.pkl')
        # se_df = pd.read_csv('merged_df_property_prices.csv')
        se_df = pd.read_pickle('merged_df_property_prices.pkl')
        gdf = gpd.read_file('gdf_comm_districts.geojson')
        gdf_projected = gdf.to_crs(epsg=32612)  # corresponds to UTM Zone 12N
        return df, se_df, gdf, gdf_projected

    df, se_df, gdf, gdf_projected = load_data()

    def generate_forecasts(df):
        from sklearn.linear_model import LinearRegression
        forecasts = {}
        for comm_name in df['COMM_NAME'].unique():
            community_data = df[df['COMM_NAME'] == comm_name]
            X = community_data['ROLL_YEAR'].values.reshape(-1, 1)
            y = community_data['ASSESSED_VALUE'].values
            model = LinearRegression()
            model.fit(X, y)
            forecast_years = np.array([[2024], [2025], [2026], [2027], [2028]])
            predicted_values = model.predict(forecast_years)
            forecast_df = pd.DataFrame({
                'ROLL_YEAR': [2024, 2025, 2026, 2027, 2028],
                'ASSESSED_VALUE': predicted_values,
                'COMM_NAME': comm_name,
                'is_forecast': True
            })
            forecasts[comm_name] = forecast_df
        return forecasts

    # df = pd.read_pickle('Grouped_Data_ALL-Years.pkl')
    # se_df = pd.read_csv('merged_df_property_prices.csv')
    # gdf = gpd.read_file('gdf_comm_districts.geojson')
    # gdf_projected = gdf.to_crs(epsg=32612)  # corresponds to UTM Zone 12N

    # Streamlit widget for multi-selection
    selected_communities = st.multiselect(
        'Select Communities',
        options=df['COMM_NAME'].unique(),
        # default=df['COMM_NAME'].unique()  # Default to all communities
        default=[df['COMM_NAME'].unique()[0]]  # Default to the first community

    )
    # Filter the DataFrame and GeoDataFrame based on selected communities
    @st.cache_data
    def filter_data(df, selected_communities):
        return df[df['COMM_NAME'].isin(selected_communities)]

    filtered_df = filter_data(df, selected_communities)

    # filtered_df = df[df['COMM_NAME'].isin(selected_communities)]
    gdf['is_selected'] = gdf['NAME'].isin(selected_communities)

    # Create the Plotly plot for the selected communities

    # @st.cache_data
    # def create_plot(filtered_df):
    #     # Generate the plot based on filtered_df
    #     fig = px.line(filtered_df, x='ROLL_YEAR', y='ASSESSED_VALUE', color='COMM_NAME',
    #             labels={'ROLL_YEAR': 'Year', 'ASSESSED_VALUE': 'Average Assessed Value', 'COMM_NAME': 'Community'},
    #             title='Average Assessed Value per Community Over Years')
    #     fig.update_layout(title_text="Assessed Value", title_x=0.3, width=800, height=600)

    #     return fig


    @st.cache_data
    # def create_plot(filtered_df, forecasts):
    #     # Append the forecast data to the filtered dataframe
    #     for comm_name, forecast_df in forecasts.items():
    #         if comm_name in filtered_df['COMM_NAME'].unique():
    #             filtered_df = pd.concat([filtered_df, forecast_df], ignore_index=True)

    #     # Generate the plot
    #     fig = px.line(filtered_df, x='ROLL_YEAR', y='ASSESSED_VALUE', color='COMM_NAME',
    #                 labels={'ROLL_YEAR': 'Year', 'ASSESSED_VALUE': 'Average Assessed Value', 'COMM_NAME': 'Community'},
    #                 title='Average Assessed Value per Community Over Years')

    #     # Differentiate forecasted data with a dotted line
    #     for comm_name in forecasts.keys():
    #         forecast_data = filtered_df[(filtered_df['COMM_NAME'] == comm_name) & (filtered_df['is_forecast'] == True)]
    #         if not forecast_data.empty:
    #             fig.add_scatter(x=forecast_data['ROLL_YEAR'], y=forecast_data['ASSESSED_VALUE'], mode='lines',
    #                             line=dict(dash='dot'), name=f"{comm_name} Forecast")

    #     fig.update_layout(title_text="Assessed Value", title_x=0.3, width=800, height=600)
    #     return fig

    @st.cache_data
    def create_plot(filtered_df, forecasts):
        # Determine the full range of years for the x-axis
        all_years = list(filtered_df['ROLL_YEAR'].unique())
        forecast_years = [2024, 2025, 2026, 2027, 2028]  # Update this if your forecast years are different
        all_years.extend(forecast_years)
        all_years = sorted(set(all_years))

        # Start generating the plot with historical data
        fig = px.line(filtered_df, x='ROLL_YEAR', y='ASSESSED_VALUE', color='COMM_NAME',
                    labels={'ROLL_YEAR': 'Year', 'ASSESSED_VALUE': 'Average Assessed Value', 'COMM_NAME': 'Community'},
                    title='Average Assessed Value per Community Over Years')

        # Add forecast data as dotted lines
        for comm_name in forecasts.keys():
            forecast_data = forecasts[comm_name]
            if comm_name in filtered_df['COMM_NAME'].unique():
                fig.add_scatter(x=forecast_data['ROLL_YEAR'], y=forecast_data['ASSESSED_VALUE'], mode='lines',
                                line=dict(dash='dot'), name=f"{comm_name} Forecast")

        # Update layout
        fig.update_layout(title_text="Assessed Value", title_x=0.3, width=800, height=600, 
                        xaxis=dict(tickmode='array', tickvals=all_years, ticktext=[str(year) for year in all_years]))

        return fig



    # fig = create_plot(filtered_df)
    # Generate forecasts
    forecasts = generate_forecasts(df)
    fig = create_plot(filtered_df, forecasts)
    # st.plotly_chart(fig)

    # fig = px.line(filtered_df, x='ROLL_YEAR', y='ASSESSED_VALUE', color='COMM_NAME',
    #               labels={'ROLL_YEAR': 'Year', 'ASSESSED_VALUE': 'Average Assessed Value', 'COMM_NAME': 'Community'},
    #               title='Average Assessed Value per Community Over Years')
    # fig.update_layout(title_text="Assessed Value", title_x=0.3, width=800, height=600)

    # st.plotly_chart(fig)
    fig1 = px.choropleth_mapbox(gdf, geojson=gdf.geometry.__geo_interface__,
                                locations=gdf.index,
                                color='is_selected',
                                center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()},
                                mapbox_style="stamen-toner",
                                zoom=9,
                                hover_name='NAME',
                                color_discrete_map={True: "yellow", False: "lightgray"})
    fig1.update_layout(title_text="Community Map", title_x=0.3, width=800, height=600)

    # Create columns for side by side layout
    col1, col2 = st.columns([1, 1])

    # Use columns to display figures
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Check if the filtered GeoDataFrame is not empty
        if not gdf.empty:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.write("No communities selected or community data not available.")

    ####################
    # ---------------------------
    # Function to categorize variables based on their range
    def categorize_variables(se_df, selected_variables):
        variable_categories = {'primary': [], 'secondary': []}
        ranges = []

        # Calculate the range of each variable
        for variable in selected_variables:
            min_val = se_df[variable].min()
            max_val = se_df[variable].max()
            var_range = max_val - min_val
            ranges.append((variable, var_range))

        # Sort variables based on range
        sorted_ranges = sorted(ranges, key=lambda x: x[1])

        # Split variables into two groups
        median_index = len(sorted_ranges) // 2
        for i, (variable, _) in enumerate(sorted_ranges):
            if i < median_index:
                variable_categories['primary'].append(variable)
            else:
                variable_categories['secondary'].append(variable)

        return variable_categories

    # Streamlit widget for multi-selection
    selected_variables = st.multiselect(
        'Select Factors',
        options=se_df.columns[1:],  # All column names excluding 'year_month'
        default=se_df.columns[1]  # Default to the first variable
    )

    # Categorize variables
    variable_categories = categorize_variables(se_df, selected_variables)

    # Create a Plotly figure
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces for primary variables
    for variable in variable_categories['primary']:
        fig2.add_trace(go.Scatter(x=se_df['year_month'], y=se_df[variable], name=variable), secondary_y=False)

    # Add traces for secondary variables
    for variable in variable_categories['secondary']:
        fig2.add_trace(go.Scatter(x=se_df['year_month'], y=se_df[variable], name=variable), secondary_y=True)

    # Update layout
    fig2.update_layout(
        title_text="Selected Variables Over Time",
        xaxis_title="Year-Month",
        width=1600,  # Width of the figure in pixels
        height=600  # Height of the figure in pixels
    )

    # Update y-axes titles
    fig2.update_yaxes(title_text="Primary Axis", secondary_y=False)
    fig2.update_yaxes(title_text="Secondary Axis", secondary_y=True)

    # Display the plot in Streamlit
    st.plotly_chart(fig2)



    # ----------------------
    # st.markdown('### Social Economic Factors')

    # # Streamlit widget for multi-selection
    # selected_variables = st.multiselect(
    #     'Select Factors',
    #     options=se_df.columns[1:],  # All column names excluding 'year_month'
    #     default=se_df.columns[1]  # Default to the first variable
    # )

    # # Create a Plotly figure
    # fig2 = go.Figure()

    # # Add traces for selected variables
    # for variable in selected_variables:
    #     fig2.add_trace(go.Scatter(x=se_df['year_month'], y=se_df[variable], name=variable))

    # # Update layout
    # fig2.update_layout(
    #     title_text="Selected Variables Over Time",
    #     xaxis_title="Year-Month",
    #     yaxis_title="Value",
    #     width=1600,  # Width of the figure in pixels
    #     height=600  # Height of the figure in pixels
    # )

    # # Display the plot in Streamlit
    # st.plotly_chart(fig2)

    ####################
    # Create a subplot figure
    fig3 = make_subplots(rows=3, cols=2, specs=[[{'secondary_y': True}, {'secondary_y': True}],
                                                [{'secondary_y': True}, {'secondary_y': True}],
                                                [{'secondary_y': True}, {'secondary_y': True}], ],
                         subplot_titles=['Employment and Unemployment', 'Consumer Price Index', 'Building Construction Price Index', 'Net Migration',
                                         '5 year Mortgage rate vs Average House Price', 'New Property Developments and WTI'])

    # Employment and Unemployment
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Employment'], name='Employment'), row=1, col=1,
                   secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Labour force'], name='Labour force'), row=1, col=1,
                   secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Full-time employment'], name='Full-time Employment'),
                   row=1, col=1, secondary_y=False)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Part-time employment'], name='Part-time Employment'), row=1, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Unemployment'], name='Unemployment'), row=1, col=1,
                   secondary_y=True)
    fig3.update_yaxes(title_text="Employment", secondary_y=False, row=1, col=1)
    fig3.update_yaxes(title_text="Unemployment", secondary_y=True, row=1, col=1)

    # # Employment Rate and Unemployment Rate
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Employment rate'], name='Employment Rate'), row=1, col=2, secondary_y=False)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Unemployment rate'], name='Unemployment Rate'), row=1, col=2, secondary_y=True)
    # fig3.update_yaxes(title_text="Employment rate", secondary_y=False, row=1, col=2)
    # fig3.update_yaxes(title_text="Unemployment rate", secondary_y=True, row=1, col=2)

    # BCPI Variables
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Total'], name='Annual BCPI Total'), row=2,
                   col=1)
    fig3.add_trace(
        go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Excluding_Energy'], name='Annual BCPI Excluding Energy'),
        row=2, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Energy'], name='Annual BCPI Energy'), row=2,
                   col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Metals_and_Minerals'],
                              name='Annual_BCPI_Metals_and_Minerals'), row=2, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Forestry'], name='Annual BCPI Forestry'),
                   row=2, col=1)
    fig3.add_trace(
        go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Agriculture'], name='Annual BCPI Agriculture'), row=2,
        col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Fish'], name='Annual BCPI Fish'), row=2,
                   col=1)

    # CPI Variables
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Total_CPI'], name='Total_CPI'), row=2, col=2)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Total_CPI_seasonally_adjusted'], name='Total_CPI_seasonally_adjusted'), row=2, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_trim'], name='Consumer Price Index - Trim'), row=1, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_median'], name='Consumer Price Index - Median'), row=1, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_common'], name='Consumer Price Index - Common'), row=1, col=2)

    # Population
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Population'], name='Population'), row=3, col=1, secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['net_migration'], name='Net Migration'), row=2, col=2,
                   secondary_y=False)
    # Update y-axis titles
    # fig3.update_yaxes(title_text="Population", secondary_y=False, row=3, col=1)
    # fig3.update_yaxes(title_text="Net migration", secondary_y=True, row=3, col=1)

    # Construction WTI
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['housing_starts'], name='New Property Developments'), row=3, col=2,
                   secondary_y=False)
    # 'WTI' on the secondary y-axis
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['WTI'], name='WTI'), row=3, col=2, secondary_y=True)
    # Update y-axis titles
    fig3.update_yaxes(title_text="New Property Developments", secondary_y=False, row=3, col=2)
    fig3.update_yaxes(title_text="WTI", secondary_y=True, row=3, col=2)

    # House price and mortagge rate
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Home_Prices_Calgary'], name='Average House Prices - Calgary'), row=3,
                   col=1, secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['5_year_mortgage_rate'], name='5-year Mortgage Rate'),
                   row=3, col=1, secondary_y=True)
    # Update y-axis titles
    fig3.update_yaxes(title_text="Home_Prices_Calgary", secondary_y=False, row=3, col=1)
    fig3.update_yaxes(title_text="5_year_mortgage_rate", secondary_y=True, row=3, col=1)

    # Update layout
    fig3.update_layout(height=1000, width=1600, title_text="Time Series Analysis")
    # fig3.show()

    # Display the figure
    st.plotly_chart(fig3)

# Content for Tab 4
with tab4:

    if "estimated_home_price" in st.session_state:
        # Retrieve and assign to a variable
        estimated_home_price_tab4 = st.session_state['estimated_home_price']

        # Now you can use this variable as needed
        # st.write(f"Estimated Home Price from Financial Fit Finder Tab: ${estimated_home_price_tab4:,.2f}")
        st.markdown(f"""
                <style>
                    .custom-text3 {{
                        font-size: 18px;  /* Font size for the entire paragraph */
                        color: yellow;
                        margin-bottom: -10px;  /* Reduce bottom margin */
                    }}
                    .selectbox-label {{
                        margin-top: -10px;  /* Reduce top margin */
                    }}
                </style>
                <p class='custom-text2'>Estimated Home Price from Financial Fit Finder Tab: ${estimated_home_price_tab4:,.2f}</p>
                """, unsafe_allow_html=True)
        # Other operations using estimated_home_price_tab4
    else:
        # st.write("Estimated home price is not calculated yet. Please go to Financial Fit Finder Tab.")
        st.markdown(f"""
                    <style>
                        .custom-text4 {{
                            font-size: 18px;  /* Font size for the entire paragraph */
                            color: red;
                            margin-bottom: -10px;  /* Reduce bottom margin */
                        }}
                        .selectbox-label {{
                            margin-top: -10px;  /* Reduce top margin */
                        }}
                    </style>
                    <p class='custom-text2'>Estimated home price is not calculated yet. Please go to Financial Fit Finder Tab.</p>
                    """, unsafe_allow_html=True)

        estimated_home_price_tab4 = 500000
        # price_predict = estimated_home_price_tab4


    def create_map(comms, comms_sub):

        colormap = cm.linear.YlGnBu_09.to_step(data=comms_sub['COMM_SLT'], method='quant',
                                               quantiles=[0, 0.1, 0.75, 0.9, 0.98, 1])

        m = folium.Map(location=[51.049999, -114.066666], zoom_start=10, tiles=None)
        folium.TileLayer('CartoDB positron', name="Light Map", control=False).add_to(m)
        colormap.caption = "# of Affordable Residental Properties in Calgary Communities"
        style_function = lambda x: {"weight": 0.5,
                                    'color': 'black',
                                    'fillColor': colormap(x['properties']['COMM_SLT']),
                                    'fillOpacity': 0.75}
        highlight_function = lambda x: {'fillColor': '#000000',
                                        'color': '#000000',
                                        'fillOpacity': 0.5,
                                        'weight': 0.1}
        RES = folium.features.GeoJson(
            comms_sub,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(fields=['COMMUNITY_NAME', 'PROP', 'COMM_SLT'],
                                                   aliases=['Community: ',
                                                            'Proportion of affordable residences for YOU: ',
                                                            'Number of affordable residences for YOU: '],
                                                   style=(
                                                       "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
                                                   sticky=True
                                                   )
        )
        colormap.add_to(m)
        m.add_child(RES)
        return m


    def get_properties(sub, comms, max_price, low_end):
        sub = sub[((sub['VALUE_2023'] >= low_end) & (sub['VALUE_2023'] <= max_price)) &
                  ((sub['VALUE_2024'] >= low_end) & (sub['VALUE_2024'] <= max_price)) &
                  ((sub['VALUE_2025'] >= low_end) & (sub['VALUE_2025'] <= max_price)) &
                  ((sub['VALUE_2026'] >= low_end) & (sub['VALUE_2026'] <= max_price))
                  ]
        sub['COMM_SLT'] = sub.groupby(['COMMUNITY_NAME'])['PROPERTY_ID'].transform('nunique')
        sub = round(sub, 3)
        sub['PROP'] = round(sub['COMM_SLT'] / sub['COMM_ALL'], 3)

        sub_trunc = sub[['COMMUNITY_NAME', 'COMM_ALL', 'COMM_SLT', 'PROP']].drop_duplicates()

        # comms = comms[['name', 'geometry']].rename(columns={'name': 'COMMUNITY_NAME'})
        comms_sub = comms.merge(sub_trunc, on="COMMUNITY_NAME", how='left')
        comms_sub = comms_sub.fillna(0)
        map = create_map(comms, comms_sub)
        return sub, map


    def dataframe_with_selections(df):
        '''
        Returns the dataframe with the user-selected rows check-boxed
        Adapted from github Tutorial: https://docs.streamlit.io/knowledge-base/using-streamlit/how-to-get-row-selections
        '''
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Select", False)
        # Get user row selections
        edited_df = st.data_editor(df_with_selections, hide_index=True,
                                   column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                                   disabled=df.columns,
                                   )
        # Filter the dataframe using the temporary column, then drop the column
        selected_rows = edited_df[edited_df.Select]
        return selected_rows.drop('Select', axis=1)


    def filter_dataframe(df):
        """
        Allows users filter columns
        Adapted from github Tutorial: https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/
        """
        modify = st.checkbox("Add filters")
        if not modify:
            return df
        df = df.copy()

        modification_container = st.container()

        with modification_container:
            filter_columns = st.multiselect("Filter on", df.columns[:-2])
            for column in filter_columns:
                left, right = st.columns((1, 20))
                if is_categorical_dtype(df[column]):
                    user_cat_input = right.multiselect(f"Values for {column}", df[column].unique(),
                                                       default=list(df[column].unique()), )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = int(df[column].min())
                    _max = int(df[column].max())
                    step = int((_max - _min) / 1000)
                    user_num_input = right.slider(f"Values for {column}", min_value=_min, max_value=_max,
                                                  value=(_min, _max), step=step, )
                    df = df[df[column].between(*user_num_input)]
                else:
                    user_text_input = right.text_input(f"Enter value for {column}", )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input.upper())]
        return df

# ---------------
    # Initialize session state variables for map state
    if 'map_zoom' not in st.session_state:
        st.session_state['map_zoom'] = 10  # Default zoom level
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = [51.049999, -114.066666]  # Default center coordinates

    # Modified property_map function
    def property_map(mini_df, sub, comms):
        # Define map center and zoom
        if (len(mini_df) > 0) & (len(mini_df) < 25):
            data_point = list(mini_df.COMMUNITY_NAME.unique())
            x_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.x.mean()
            y_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.y.mean()
            map_center = [y_val, x_val]
            map_zoom = 12  # Zoom when specific data points are selected
        else:
            map_center = st.session_state['map_center']
            map_zoom = st.session_state['map_zoom']

        m2 = folium.Map(location=map_center, zoom_start=map_zoom)
        # m2 = folium.Map(location=[y_val, x_val], zoom_start=12)
        folium.TileLayer('openstreetmap').add_to(m2)
        folium.LayerControl().add_to(m2)
        for i in range(len(mini_df)):
            folium.Marker(location=[mini_df.iloc[i]["LATITUDE"], mini_df.iloc[i]["LONGITUDE"]],
                            popup='ADDRESS: ' + mini_df.iloc[i]['ADDRESS'] + ', CURRENT VALUE: $' + str(
                                mini_df.iloc[i]['CURRENT_VALUE']),
                            icon=folium.Icon(color='blue')
                            ).add_to(m2)
        # Rest of the map setup code...

        return m2

#----------------------


    # def property_map(mini_df, sub, comms):
    #     if (len(mini_df) > 0) & (len(mini_df) < 25):
    #         data_point = list(mini_df.COMMUNITY_NAME.unique())
    #         x_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.x.mean()
    #         y_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.y.mean()

    #         m2 = folium.Map(location=[y_val, x_val], zoom_start=12)
    #         folium.TileLayer('openstreetmap').add_to(m2)
    #         folium.LayerControl().add_to(m2)
    #         formatter = "function(num) {return L.Util.formatNum(num,3) + ' ° ';};"
    #         MousePosition(
    #             position='topright',
    #             separator=' | ',
    #             empty_string='NaN',
    #             lng_first=True,
    #             num_digits=20,
    #             prefix='Coordinates:',
    #             lat_formatter=formatter,
    #             lng_formatter=formatter
    #         ).add_to(m2)
    #         for i in range(len(mini_df)):
    #             folium.Marker(location=[mini_df.iloc[i]["LATITUDE"], mini_df.iloc[i]["LONGITUDE"]],
    #                           popup='ADDRESS: ' + mini_df.iloc[i]['ADDRESS'] + ', CURRENT VALUE: $' + str(
    #                               mini_df.iloc[i]['VALUE_2023']),
    #                           icon=folium.Icon(color='blue')
    #                           ).add_to(m2)
    #         return m2
    #     else:
    #         m2 = folium.Map(location=[51.049999, -114.066666], zoom_start=10)
    #         folium.TileLayer('CartoDB positron', name="Light Map").add_to(m2)
    #         folium.LayerControl().add_to(m2)
    #         formatter = "function(num) {return L.Util.formatNum(num,3) + ' ° ';};"
    #         MousePosition(
    #             position='topright',
    #             separator=' | ',
    #             empty_string='NaN',
    #             lng_first=True,
    #             num_digits=20,
    #             prefix='Coordinates:',
    #             lat_formatter=formatter,
    #             lng_formatter=formatter
    #         ).add_to(m2)
    #         return m2


    properties = pd.read_pickle('Calgary Property Data.pkl')
    properties = properties.rename(columns={'COMM_NAME': 'COMMUNITY_NAME'})
    communities = gpd.read_file(
        'geo_export_439b7cc6-4dd0-4905-af0d-7c9d5901f392.shp')
    communities = communities[['name', 'geometry']].rename(columns={'name': 'COMMUNITY_NAME'})

    col1, col2, col3 = st.columns([2, 4, 2])

    with col1.container():
        st.write("")
    with col2.container():

        st.markdown('<h4 style="color: #FFFDE7;">Calgary Custom Affordability Map</h4>', unsafe_allow_html=True)
        st.markdown(
            "Unveil personalized affordable housing counts with 'Calgary's Custom Affordability Map'. Each community's data reflects properties within your budget, guiding you to your ideal locale.")
        st.write(" ")

        price_predict = estimated_home_price_tab4
        # price_predict = st.number_input('Home Purchase Price', min_value=0.0, value=500000.0, step=10000.0,
        #                                 format='%.2f',
        #                                 help='Enter your maximum home purchase price')
        low_end = price_predict * 0.75
        property_list, map = get_properties(properties, communities, price_predict, low_end)
        property_list = property_list.reset_index(drop=True)
        # folium_static(map)
        map.fit_bounds(map.get_bounds())  # This ensures that the map is centered and zoomed appropriately
        folium_static(map, width=1200, height=700)  # Adjust the width and height as necessary
    with col3.container():
        st.write("")

    col4, col5, col6, col7, col8 = st.columns([0.2, 1.3, 0.1, 1, 0.3])

    with col4.container():
        st.write("")

    with col5.container():
        st.markdown('<h4 style="color: #FFFDE7;">Select & Explore Properties</h4>', unsafe_allow_html=True)
        st.write(" \n\n")
        selection = dataframe_with_selections(filter_dataframe(property_list[['ADDRESS', 'COMMUNITY_NAME', 'VALUE_2023',
                                                                              'LATITUDE', 'LONGITUDE']].rename(columns={'VALUE_2023':'CURRENT_VALUE'})))
    with col6.container():
        st.write("")

    with col7.container():
        st.markdown('<h4 style="color: #FFFDE7;">Property Details</h4>', unsafe_allow_html=True)
        st.markdown(
            "Utilize the 'Select & Explore' feature to interactively choose specific locations on the Calgary map. This tool empowers you to focus on communities of interest and discover available properties tailored to your preferences.")
        st.write(" ")
        folium_static(property_map(selection, property_list, communities), width=800, height=400)

    with col8.container():
        st.write("")

