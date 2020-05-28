from flask import jsonify
from pony.orm import db_session

from util.decorators import require_json
from util.exceptions import InvalidAuthHeaderException, AuthorizationException
from constant.error import AUTH_HEADER_MISSING, INVALID_TOKEN, UNTRUSTED_IP, INCORRECT_ANSWERS
from constant.security_questions import questions
from db import AccessToken


@db_session
def list_challenges(request):
    try:
        token = AccessToken.from_header(request.headers.get("Authorization"))
    except InvalidAuthHeaderException:
        return AUTH_HEADER_MISSING.dual
    if token is None:
        return INVALID_TOKEN.dual

    account = token.client_token.account
    return_questions = []
    for question in account.security_questions:
        return_questions.append({
            "answer": {
                "id": question.id
            },
            "question": {
                "id": question.question_id,
                "question": questions[question.question_id]
            }
        })
    return jsonify(return_questions), 200


@db_session
@require_json
def location(request):
    try:
        token = AccessToken.from_header(request.headers.get("Authorization"))
    except InvalidAuthHeaderException:
        return AUTH_HEADER_MISSING.dual
    if token is None:
        return INVALID_TOKEN.dual

    account = token.client_token.account

    if request.method == "GET":
        if account.does_trust_ip(request.remote_addr):
            return "", 204
        return UNTRUSTED_IP.dual

    elif request.method == "POST":
        if not isinstance(request.json, list):
            return INCORRECT_ANSWERS

        try:
            answers_correct = account.check_answers(request.json)
        except (AuthorizationException, KeyError) as e:
            return INCORRECT_ANSWERS.dual

        if answers_correct:
            account.trust_ip(request.remote_addr)
            return "", 204
        else:
            return INCORRECT_ANSWERS.dual
