def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int
) -> dict:

    if principal <= 0:
        raise ValueError(
            "Loan amount must be greater than zero."
        )

    if annual_rate < 0:
        raise ValueError(
            "Interest rate cannot be negative."
        )

    if tenure_months <= 0:
        raise ValueError(
            "Tenure must be greater than zero."
        )

    monthly_rate = annual_rate / 12 / 100

    if monthly_rate == 0:

        emi = principal / tenure_months

    else:

        emi = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** tenure_months
            / (
                (1 + monthly_rate) ** tenure_months
                - 1
            )
        )

    total_payment = emi * tenure_months

    total_interest = (
        total_payment - principal
    )

    return {

        "loan_amount": round(
            principal,
            2
        ),

        "interest_rate": round(
            annual_rate,
            2
        ),

        "tenure_months": tenure_months,

        "monthly_emi": round(
            emi,
            2
        ),

        "total_payment": round(
            total_payment,
            2
        ),

        "total_interest": round(
            total_interest,
            2
        )
    }