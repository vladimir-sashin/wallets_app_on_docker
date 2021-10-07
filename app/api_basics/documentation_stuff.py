from api_basics.errors_exceptions import (
    INSUFFICIENT_FUNDS_ERROR,
    RECIPIENT_DOESNT_EXIST_ERROR,
    RECIPIENT_IS_SENDER_ERROR,
    TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR,
)
from drf_spectacular.utils import OpenApiExample

CREATE_WALLET_REQUEST_EXAMPLE = OpenApiExample(
    "Valid request example",
    description="Note that 'balance' field is not included in the request "
    "body. This field will be ignored anyway.",
    value={"name": "my_wallet123"},
    request_only=True,
    response_only=False,
)

MAKE_DEPOSIT_REQUEST = OpenApiExample(
    "Make Deposit request example",
    description="Deposit amount is the only field that should be in the request body,"
    " both float and string types are acceptable.",
    value={"amount": 500.23},
    request_only=True,
    status_codes=["200"],
)

TRANSACTION_RESPONSE = OpenApiExample(
    "Make Deposit / Make Transfer success response example",
    value={"transaction_status": "success", "new_balance": "1900.32"},
    response_only=True,
    status_codes=["200"],
)

TRANSACTION_NEGATIVE_ZERO_AMOUNT_RESPONSE = OpenApiExample(
    "Make Deposit / Make Transfer response if amount is" " negative or zero",
    value={"amount": [TRANSACTION_AMOUNT_ZERO_NEGATIVE_ERROR]},
    response_only=True,
    status_codes=["400"],
)

MAKE_TRANSFER_REQUEST = OpenApiExample(
    "Make Transfer request example",
    description="'amount' and 'recipient' fields are mandatory.",
    value={"amount": 100.21, "recipient": "wallet_2"},
    request_only=True,
    status_codes=["200"],
)

INSUFFICIENT_FUNDS_RESPONSE = OpenApiExample(
    "Make Transfer response if 'amount' is > sender's balance",
    value={"amount": [INSUFFICIENT_FUNDS_ERROR]},
    response_only=True,
    status_codes=["400"],
)

RECIPIENT_IS_SENDER_RESPONSE = OpenApiExample(
    "Make Transfer response if 'recipient' = sender",
    value={"recipient": [RECIPIENT_IS_SENDER_ERROR]},
    response_only=True,
    status_codes=["400"],
)

RECIPIENT_DOESNT_EXIST_RESPONSE = OpenApiExample(
    "Make Transfer response if 'recipient' doesn't exist",
    value={"recipient": [RECIPIENT_DOESNT_EXIST_ERROR]},
    response_only=True,
    status_codes=["400"],
)

history_csv_response_example = (
    "amount,balance_after,balance_before,id,recipient,sender,timestamp,transaction_type,wallet\n"
    "100.00,900.00,800.00,14,wallet_10,wallet_11,2021-10-07T13:01:21.292678Z,CRED,wallet_10\n"
    "200.00,800.00,1000.00,11,wallet_11,wallet_10,2021-10-07T12:58:35.304003Z,DEB,wallet_10\n"
    "1000.00,1000.00,0.00,9,wallet_10,,2021-10-07T12:58:14.168449Z,CRED,wallet_10"
)

history_json_response_example = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 14,
            "wallet": "wallet_10",
            "sender": "wallet_11",
            "recipient": "wallet_10",
            "amount": "100.00",
            "transaction_type": "CRED",
            "balance_before": "800.00",
            "balance_after": "900.00",
            "timestamp": "2021-10-07T13:01:21.292678Z",
        },
        {
            "id": 11,
            "wallet": "wallet_10",
            "sender": "wallet_10",
            "recipient": "wallet_11",
            "amount": "200.00",
            "transaction_type": "DEB",
            "balance_before": "1000.00",
            "balance_after": "800.00",
            "timestamp": "2021-10-07T12:58:35.304003Z",
        },
        {
            "id": 9,
            "wallet": "wallet_10",
            "sender": None,
            "recipient": "wallet_10",
            "amount": "1000.00",
            "transaction_type": "CRED",
            "balance_before": "0.00",
            "balance_after": "1000.00",
            "timestamp": "2021-10-07T12:58:14.168449Z",
        },
    ],
}

GET_HISTORY_CSV_RESPONSE = OpenApiExample(
    "Get History csv response example",
    value=history_csv_response_example,
    media_type="text/csv",
)

GET_HISTORY_JSON_RESPONSE = OpenApiExample(
    "Get History json response example",
    value=history_json_response_example,
    media_type="application/json",
)
