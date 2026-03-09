try:
	from backend.api.main import app
except ModuleNotFoundError:
	from api.main import app
