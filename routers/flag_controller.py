from fastapi import APIRouter
from repository.flag_repository import Flag_repository
from service.flag_service import Flag_service
from domain.schemas import CreateFlag, CreateFlagResponse, UpdateFlagStatus, UpdateFlagResponse, FlagResponse

router = APIRouter()

@router.post("/flag/init")
def iniciar_flag(flag: CreateFlag):
	flag_repo = Flag_repository()
	flag_service = Flag_service(flag_repo)
	response = flag_service.iniciar_nova_flag(flag)
	return response

@router.put("/flag")
def atualizar_flag(status: UpdateFlagStatus):
	flag_repo = Flag_repository()
	flag_service = Flag_service(flag_repo)
	response = flag_service.atualizar_status_flag(status)
	return response

@router.get("/flag/{task_id}")
def buscar_flag(task_id: str):
	flag_repo = Flag_repository()
	flag_service = Flag_service(flag_repo)
	response = flag_service.buscar_flag(task_id)
	return response

@router.get("/flag")
def buscar_flags():
	flag_repo = Flag_repository()
	flag_service = Flag_service(flag_repo)
	response = flag_service.obter_todas_flags()
	return response

@router.delete("/flag/{task_id}")
def remover_flag(task_id: str):
	flag_repo = Flag_repository()
	flag_service = Flag_service(flag_repo)
	response = flag_service.remover_flag(task_id)
	return response

