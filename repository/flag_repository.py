import os
from typing import Optional
from supabase import create_client, Client
from domain.enum import FlagStatusEnum
from datetime import datetime
from domain.schemas import (
    CreateFlag,
    FlagResponse,
    UpdateFlagStatus,
    UpdateFlagResponse,
)
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("FLAG_SUPABASE_URL")
SUPABASE_KEY = os.getenv("FLAG_SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class Flag_repository:
    @staticmethod
    def registrar_inicio_nova_flag(flag: CreateFlag) -> FlagResponse:
        dados_insercao = {
            "tb_flags_task_id": flag.tb_flags_task_id,
            "tb_flags_task_user_id": flag.tb_flags_task_user_id,
            "tb_flags_status": FlagStatusEnum.ENTREGA_PARCIAL,
        }
        resposta = supabase.table("tb_flags_register").insert(dados_insercao).execute()
        return FlagResponse(**resposta.data[0])

    @staticmethod
    def mudar_status_flag(payload: UpdateFlagStatus) -> UpdateFlagResponse:
        data_brasil = datetime.now().strftime("%d/%m/%Y")
        dados_atualizacao = {
            "tb_flags_status": payload.tb_flags_status.value,
            "tb_flags_updated_at": data_brasil,
        }
        resposta = (
            supabase.table("tb_flags_register")
            .update(dados_atualizacao)
            .eq("tb_flags_task_id", payload.tb_flags_task_id)
            .execute()
        )
        if not resposta.data:
            raise ValueError(
                f"Nenhuma flag encontrada para a task {payload.tb_flags_task_id}"
            )
        registro = resposta.data[0]
        return UpdateFlagResponse(
            tb_flags_status=FlagStatusEnum(registro["tb_flags_status"]),
            tb_updated_at=registro["tb_flags_updated_at"],
        )

    @staticmethod
    def buscar_registro_flag(task_id: str) -> FlagResponse:
        resposta = (
            supabase.table("tb_flags_register")
            .select("*")
            .eq("tb_flags_task_id", task_id)
            .execute()
        )
        if not resposta.data:
            return []
        return FlagResponse(**resposta.data[0])

    @staticmethod
    def buscar_todos_registros() -> list[FlagResponse]:
        resposta = supabase.table("tb_flags_register").select("*").execute()
        if not resposta.data:
            return []
        return [FlagResponse(**registro) for registro in resposta.data]
