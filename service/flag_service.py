from domain.schemas import CreateFlag, UpdateFlagStatus, FlagResponse, UpdateFlagResponse
from repository.flag_repository import Flag_repository

class Flag_service:
    def __init__(self, repository: Flag_repository):
        self.repository = repository

    def iniciar_nova_flag(self, task: CreateFlag) -> FlagResponse:
        return self.repository.registrar_inicio_nova_flag(task)

    def atualizar_status_flag(self, payload: UpdateFlagStatus) -> UpdateFlagResponse:
        return self.repository.mudar_status_flag(payload)

    def buscar_flag(self, task_id: str) -> FlagResponse:
        return self.repository.buscar_registro_flag(task_id)

    def obter_todas_flags(self) -> list[FlagResponse]:
        return self.repository.buscar_todos_registros()
