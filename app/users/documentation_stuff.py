from drf_spectacular.utils import OpenApiExample

BAD_REQUEST_RESPONSE = OpenApiExample(
    "Bad Request",
    description="User already exists",
    value={"username": ["A user with that username already exists."]},
    response_only=True,
    status_codes=["400"],
)
