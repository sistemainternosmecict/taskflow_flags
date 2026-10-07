from datetime import datetime, timezone
from typing import Optional, Union
from sqlalchemy import Column, BigInteger, String
from domain.enum import FlagStatusEnum
from domain.schemas import (
    CreateFlag,
    FlagResponse,
    UpdateFlagStatus,
    UpdateFlagResponse,
)
from repository.database import Base, get_db_session


class FlagModel(Base):
    __tablename__ = "tb_flags_register"

    tb_flags_id = Column(BigInteger, primary_key=True, autoincrement=True)
    tb_flags_created_at = Column(String(255), nullable=True)
    tb_flags_task_id = Column(String(255), nullable=True)
    tb_flags_task_user_id = Column(String(255), nullable=True)
    tb_flags_status = Column(String(255), nullable=True)
    tb_flags_updated_at = Column(String(255), nullable=True)

    def to_response(self) -> FlagResponse:
        return FlagResponse(
            tb_flags_id=self.tb_flags_id,
            tb_flags_created_at=self.tb_flags_created_at or "",
            tb_flags_task_id=self.tb_flags_task_id or "",
            tb_flags_task_user_id=self.tb_flags_task_user_id or "",
            tb_flags_status=FlagStatusEnum(self.tb_flags_status),
            tb_flags_updated_at=self.tb_flags_updated_at,
        )


class Flag_repository:
    @staticmethod
    def registrar_inicio_nova_flag(flag: CreateFlag) -> FlagResponse:
        with get_db_session() as session:
            nova_flag = FlagModel(
                tb_flags_task_id=flag.tb_flags_task_id,
                tb_flags_task_user_id=flag.tb_flags_task_user_id,
                tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
                tb_flags_created_at=datetime.now(timezone.utc).isoformat(),
                tb_flags_updated_at=None,
            )
            session.add(nova_flag)
            session.commit()
            session.refresh(nova_flag)
            return nova_flag.to_response()

    @staticmethod
    def mudar_status_flag(payload: UpdateFlagStatus) -> UpdateFlagResponse:
        data_brasil = datetime.now().strftime("%d/%m/%Y")
        with get_db_session() as session:
            registro = (
                session.query(FlagModel)
                .filter(FlagModel.tb_flags_task_id == payload.tb_flags_task_id)
                .first()
            )
            if not registro:
                raise ValueError(
                    f"Nenhuma flag encontrada para a task {payload.tb_flags_task_id}"
                )
            registro.tb_flags_status = payload.tb_flags_status.value
            registro.tb_flags_updated_at = data_brasil
            session.commit()
            session.refresh(registro)
            return UpdateFlagResponse(
                tb_flags_status=FlagStatusEnum(registro.tb_flags_status),
                tb_updated_at=registro.tb_flags_updated_at,
            )

    @staticmethod
    def buscar_registro_flag(task_id: str) -> Union[FlagResponse, list]:
        with get_db_session() as session:
            registro = (
                session.query(FlagModel)
                .filter(FlagModel.tb_flags_task_id == task_id)
                .first()
            )
            if not registro:
                return []
            return registro.to_response()

    @staticmethod
    def buscar_todos_registros() -> list[FlagResponse]:
        with get_db_session() as session:
            registros = session.query(FlagModel).all()
            if not registros:
                return []
            return [r.to_response() for r in registros]

    @staticmethod
    def buscar_flags_por_task_ids(task_ids: list[str]) -> list[FlagResponse]:
        if not task_ids:
            return []
        ids_formatados = [str(t_id) for t_id in task_ids]
        with get_db_session() as session:
            registros = (
                session.query(FlagModel)
                .filter(FlagModel.tb_flags_task_id.in_(ids_formatados))
                .all()
            )
            if not registros:
                return []
            return [r.to_response() for r in registros]

    @staticmethod
    def remover_flag(task_id: str) -> FlagResponse:
        with get_db_session() as session:
            registro = (
                session.query(FlagModel)
                .filter(FlagModel.tb_flags_task_id == task_id)
                .first()
            )
            if not registro:
                raise ValueError(f"Nenhuma flag encontrada para a task {task_id}")
            resposta = registro.to_response()
            session.delete(registro)
            session.commit()
            return resposta
