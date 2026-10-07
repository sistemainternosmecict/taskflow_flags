import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from domain.enum import FlagStatusEnum
from domain.schemas import CreateFlag, FlagResponse, UpdateFlagStatus, UpdateFlagResponse
from repository.flag_repository import Flag_repository, FlagModel


@patch("repository.flag_repository.get_db_session")
def test_registrar_inicio_nova_flag_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    dados_entrada = CreateFlag(
        tb_flags_task_id="task-123",
        tb_flags_task_user_id="user-999"
    )

    def side_effect_refresh(instance):
        instance.tb_flags_id = 1
        instance.tb_flags_created_at = "2026-07-02T12:00:00+00:00"

    mock_session.refresh.side_effect = side_effect_refresh

    resultado = Flag_repository.registrar_inicio_nova_flag(dados_entrada)

    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_id == 1
    assert resultado.tb_flags_task_id == "task-123"
    assert resultado.tb_flags_task_user_id == "user-999"
    assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@patch("repository.flag_repository.get_db_session")
def test_mudar_status_flag_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    payload_entrada = UpdateFlagStatus(
        tb_flags_task_id="task-123",
        tb_flags_status=FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO
    )

    mock_flag = FlagModel(
        tb_flags_id=1,
        tb_flags_created_at="2026-07-02T12:00:00+00:00",
        tb_flags_task_id="task-123",
        tb_flags_task_user_id="user-999",
        tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
        tb_flags_updated_at=None
    )
    mock_session.query.return_value.filter.return_value.first.return_value = mock_flag

    resultado = Flag_repository.mudar_status_flag(payload_entrada)

    assert isinstance(resultado, UpdateFlagResponse)
    assert resultado.tb_flags_status == FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO
    assert resultado.tb_updated_at == datetime.now().strftime("%d/%m/%Y")
    mock_session.commit.assert_called_once()


@patch("repository.flag_repository.get_db_session")
def test_mudar_status_flag_deve_lancar_value_error_quando_nao_encontrar_task(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    id_inexistente = "task-inexistente-404"
    payload_entrada = UpdateFlagStatus(
        tb_flags_task_id=id_inexistente,
        tb_flags_status=FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO
    )
    mock_session.query.return_value.filter.return_value.first.return_value = None

    mensagem_esperada = f"Nenhuma flag encontrada para a task {id_inexistente}"
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.mudar_status_flag(payload_entrada)

    assert str(exc_info.value) == mensagem_esperada


@patch("repository.flag_repository.get_db_session")
def test_buscar_registro_flag_deve_retornar_objeto_flag_response_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    task_id_alvo = "task-sucesso-123"
    mock_flag = FlagModel(
        tb_flags_id=99,
        tb_flags_created_at="2026-07-03T16:00:00+00:00",
        tb_flags_task_id=task_id_alvo,
        tb_flags_task_user_id="user-operacional",
        tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
        tb_flags_updated_at=None
    )
    mock_session.query.return_value.filter.return_value.first.return_value = mock_flag

    resultado = Flag_repository.buscar_registro_flag(task_id_alvo)

    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_task_id == task_id_alvo
    assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL


@patch("repository.flag_repository.get_db_session")
def test_buscar_registro_flag_vazio_deve_retornar_lista_vazia(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = None

    resultado = Flag_repository.buscar_registro_flag("task-inexistente")

    assert isinstance(resultado, list)
    assert len(resultado) == 0


@patch("repository.flag_repository.get_db_session")
def test_buscar_todos_registros_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    mock_flags = [
        FlagModel(
            tb_flags_id=1,
            tb_flags_created_at="2026-07-03T10:00:00+00:00",
            tb_flags_task_id="task-1",
            tb_flags_task_user_id="user-1",
            tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
            tb_flags_updated_at=None
        ),
        FlagModel(
            tb_flags_id=2,
            tb_flags_created_at="2026-07-03T11:30:00+00:00",
            tb_flags_task_id="task-2",
            tb_flags_task_user_id="user-2",
            tb_flags_status=FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO.value,
            tb_flags_updated_at=None
        )
    ]
    mock_session.query.return_value.all.return_value = mock_flags

    resultado = Flag_repository.buscar_todos_registros()

    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert isinstance(resultado[0], FlagResponse)
    assert resultado[0].tb_flags_id == 1
    assert resultado[0].tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
    assert resultado[1].tb_flags_id == 2
    assert resultado[1].tb_flags_status == FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO


@patch("repository.flag_repository.get_db_session")
def test_buscar_todos_registros_deve_retornar_lista_vazia_quando_banco_estiver_limpo(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.all.return_value = []

    resultado = Flag_repository.buscar_todos_registros()

    assert isinstance(resultado, list)
    assert len(resultado) == 0


@patch("repository.flag_repository.get_db_session")
def test_remover_flag_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    task_id_alvo = "task-delete-123"
    mock_flag = FlagModel(
        tb_flags_id=10,
        tb_flags_created_at="2026-07-04T10:00:00+00:00",
        tb_flags_task_id=task_id_alvo,
        tb_flags_task_user_id="user-delete-001",
        tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
        tb_flags_updated_at=None
    )
    mock_session.query.return_value.filter.return_value.first.return_value = mock_flag

    resultado = Flag_repository.remover_flag(task_id_alvo)

    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_id == 10
    assert resultado.tb_flags_task_id == task_id_alvo
    assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL

    mock_session.delete.assert_called_once_with(mock_flag)
    mock_session.commit.assert_called_once()


@patch("repository.flag_repository.get_db_session")
def test_remover_flag_deve_lancar_value_error_quando_nao_encontrar_task(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    id_inexistente = "task-inexistente-404"
    mock_session.query.return_value.filter.return_value.first.return_value = None

    mensagem_esperada = f"Nenhuma flag encontrada para a task {id_inexistente}"
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.remover_flag(id_inexistente)

    assert str(exc_info.value) == mensagem_esperada


@patch("repository.flag_repository.get_db_session")
def test_buscar_flags_por_task_ids_com_sucesso(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session

    task_ids_alvo = ["task-1", "task-2"]
    mock_flags = [
        FlagModel(
            tb_flags_id=1,
            tb_flags_created_at="2026-07-04T10:00:00+00:00",
            tb_flags_task_id="task-1",
            tb_flags_task_user_id="user-001",
            tb_flags_status=FlagStatusEnum.ENTREGA_PARCIAL.value,
            tb_flags_updated_at=None
        ),
        FlagModel(
            tb_flags_id=2,
            tb_flags_created_at="2026-07-04T11:00:00+00:00",
            tb_flags_task_id="task-2",
            tb_flags_task_user_id="user-002",
            tb_flags_status=FlagStatusEnum.DEVOLUCAO_EQUIPAMENTO.value,
            tb_flags_updated_at=None
        )
    ]
    mock_session.query.return_value.filter.return_value.all.return_value = mock_flags

    resultado = Flag_repository.buscar_flags_por_task_ids(task_ids_alvo)

    assert isinstance(resultado, list)
    assert len(resultado) == 2
    assert isinstance(resultado[0], FlagResponse)
    assert resultado[0].tb_flags_task_id == "task-1"
    assert resultado[1].tb_flags_task_id == "task-2"


def test_buscar_flags_por_task_ids_lista_vazia_retorna_vazio():
    resultado = Flag_repository.buscar_flags_por_task_ids([])
    assert resultado == []


@patch("repository.flag_repository.get_db_session")
def test_buscar_flags_por_task_ids_sem_resultados_retorna_vazio(mock_get_db_session):
    mock_session = MagicMock()
    mock_get_db_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.all.return_value = []

    resultado = Flag_repository.buscar_flags_por_task_ids(["task-inexistente"])

    assert resultado == []
