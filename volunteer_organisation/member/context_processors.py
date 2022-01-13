def load_session_info(request):

    if "id" not in request.session:
        return {}

    return {"user_name" : request.session["name"], "user_surname": request.session["surname"], "user_id": request.session["id"]}
