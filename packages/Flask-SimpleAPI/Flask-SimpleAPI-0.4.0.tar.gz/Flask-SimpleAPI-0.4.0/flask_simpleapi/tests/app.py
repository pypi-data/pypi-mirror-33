from flask_simple_api import SimpleApi, JsonResponse
import user

api = SimpleApi(__name__, api_root_path='/api')

api.register_api(user)
api.response_class = JsonResponse

api.print_urls()

api.run(host='0.0.0.0', port=5000, debug=True)
