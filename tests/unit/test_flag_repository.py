import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from domain.enum import FlagStatusEnum
from domain.schemas import CreateFlag, FlagResponse, UpdateFlagStatus, UpdateFlagResponse
from repository.flag_repository import Flag_repository

@patch("repository.flag_repository.supabase")
def test_registrar_inicio_nova_flag_com_sucesso(mock_supabase):
    dados_entrada = CreateFlag(
        tb_flags_task_id="task-123",
        tb_flags_task_user_id="user-999"
    )
    mock_dados_retorno_db = {
        "tb_flags_id": 1,
        "tb_flags_created_at": "2026-07-02T12:00:00Z",
        "tb_flags_task_id": "task-123",
        "tb_flags_task_user_id": "user-999",
        "tb_flags_status": "ENTREGA_PARCIAL",
        "tb_flags_updated_at": None
    }
    mock_execute = MagicMock()
    mock_execute.data = [mock_dados_retorno_db]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_execute

    resultado = Flag_repository.registrar_inicio_nova_flag(dados_entrada)

    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_id == 1
    assert resultado.tb_flags_task_id == "task-123"
    assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL

    mock_supabase.table.assert_called_once_with("tb_flags_register")
    mock_supabase.table.return_value.insert.assert_called_once_with({
        "tb_flags_task_id": "task-123",
        "tb_flags_task_user_id": "user-999",
        "tb_flags_status": "ENTREGA_PARCIAL"
    })

@patch("repository.flag_repository.supabase")
def test_mudar_status_flag_com_sucesso(mock_supabase):
    data_brasil = datetime.now().strftime("%d/%m/%Y")
    payload_entrada = UpdateFlagStatus(
        tb_flags_task_id="task-123",
        tb_flags_status=FlagStatusEnum.PRONTO_PARA_REVISAO
    )
    mock_dados_retorno_db = {
        "tb_flags_status": "PRONTO_PARA_REVISAO",
        "tb_flags_updated_at": data_brasil
    }
    mock_execute = MagicMock()
    mock_execute.data = [mock_dados_retorno_db]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_execute

    resultado = Flag_repository.mudar_status_flag(payload_entrada)

    assert isinstance(resultado, UpdateFlagResponse)
    assert resultado.tb_flags_status == FlagStatusEnum.PRONTO_PARA_REVISAO
    mock_supabase.table.assert_called_once_with("tb_flags_register")
    mock_supabase.table.return_value.update.assert_called_once_with({
        "tb_flags_status": "PRONTO_PARA_REVISAO",
        "tb_flags_updated_at": data_brasil
    })
    mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with(
        "tb_flags_task_id", "task-123"
    )

@patch("repository.flag_repository.supabase")
def test_buscar_registro_flag_deve_retornar_lista_de_flags(mock_supabase):
    # 1. Arrange (Preparação da simulação)
    task_id_busca = "task-abc-123"
    # Simula o banco retornando uma lista com dois registros brutos encontrados
    mock_dados_retorno_db = [
        {
            "tb_flags_id": 1,
            "tb_flags_created_at": "2026-07-03T10:00:00Z",
            "tb_flags_task_id": task_id_busca,
            "tb_flags_task_user_id": "user-1",
            "tb_flags_status": "ENTREGA_PARCIAL",
            "tb_flags_updated_at": None
        },
        {
            "tb_flags_id": 2,
            "tb_flags_created_at": "2026-07-03T11:30:00Z",
            "tb_flags_task_id": task_id_busca,
            "tb_flags_task_user_id": "user-1",
            "tb_flags_status": "PRONTO_PARA_REVISAO",
            "tb_flags_updated_at": None 
        }
    ]
    # Configura o encadeamento fluente: supabase.table().select().eq().execute()
    mock_execute = MagicMock()
    mock_execute.data = mock_dados_retorno_db
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_execute

    # 2. Act (Execução do método modificado)
    resultado = Flag_repository.buscar_todos_registros()

    # 3. Assert (Verificações)
    assert isinstance(resultado, list)
    assert len(resultado) == 2
    
    # Valida as conversões dos elementos internos para o DTO correto
    assert isinstance(resultado[0], FlagResponse)
    assert resultado[0].tb_flags_id == 1
    assert resultado[0].tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
    
    assert resultado[1].tb_flags_id == 2
    assert resultado[1].tb_flags_status == FlagStatusEnum.PRONTO_PARA_REVISAO

    # Inspeciona se a chamada ao Supabase manteve a ordem exata de métodos e parâmetros
    mock_supabase.table.assert_called_once_with("tb_flags_register")
    mock_supabase.table.return_value.select.assert_called_once_with("*")


@patch("repository.flag_repository.supabase")
def test_buscar_registro_flag_vazio_deve_retornar_lista_vazia(mock_supabase):
    # Cenário alternativo: Nenhuma linha correspondente encontrada no Postgres
    mock_execute = MagicMock()
    mock_execute.data = []  # Lista vazia simulando nenhum resultado
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute

    resultado = Flag_repository.buscar_registro_flag("task-inexistente")

    assert isinstance(resultado, list)
    assert len(resultado) == 0

@patch("repository.flag_repository.supabase")
def test_mudar_status_flag_deve_lancar_value_error_quando_nao_encontrar_task(mock_supabase):
    # 1. Arrange - Prepara os dados de entrada
    id_inexistente = "task-inexistente-404"
    payload_entrada = UpdateFlagStatus(
        tb_flags_task_id=id_inexistente,
        tb_flags_status=FlagStatusEnum.PRONTO_PARA_REVISAO
    )
    # Simula o banco respondendo com sucesso ao comando, mas retornando uma lista VAZIA []
    # Isso acontece se a linha não existir ou se o RLS bloquear o update silenciosamente
    mock_execute = MagicMock()
    mock_execute.data = []  
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_execute

    # 2. Act & Assert - Verifica se a execução lança o ValueError esperado
    mensagem_esperada = f"Nenhuma flag encontrada para a task {id_inexistente}"
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.mudar_status_flag(payload_entrada)
    # Valida se o texto da mensagem de erro está exatamente igual ao programado no repositório
    assert str(exc_info.value) == mensagem_esperada

@patch("repository.flag_repository.supabase")
def test_buscar_registro_flag_deve_retornar_objeto_flag_response_com_sucesso(mock_supabase):
    # Arrange
    task_id_alvo = "task-sucesso-123"
    
    # Simula o banco de dados retornando uma lista contendo exatamente um registro bruto
    mock_dados_db = [{
        "tb_flags_id": 99,
        "tb_flags_created_at": "2026-07-03T16:00:00Z",
        "tb_flags_task_id": task_id_alvo,
        "tb_flags_task_user_id": "user-operacional",
        "tb_flags_status": "ENTREGA_PARCIAL",
        "tb_flags_updated_at": None
    }]
    
    # Configura o encadeamento fluente com o .eq() que este método utiliza
    mock_execute = MagicMock()
    mock_execute.data = mock_dados_db
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute

    # Act
    resultado = Flag_repository.buscar_registro_flag(task_id_alvo)

    # Assert
    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_task_id == task_id_alvo
    assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
    
    # Inspeciona se a chamada encadeou corretamente os filtros no Supabase
    mock_supabase.table.assert_called_once_with("tb_flags_register")
    mock_supabase.table.return_value.select.assert_called_once_with("*")
    mock_supabase.table.return_value.select.return_value.eq.assert_called_once_with("tb_flags_task_id", task_id_alvo)


# -------------------------------------------------------------------------
# 2. TESTE DE UNIDADE: buscar_todos_registros -> Retorno de Lista Vazia []
# -------------------------------------------------------------------------
@patch("repository.flag_repository.supabase")
def test_buscar_todos_registros_deve_retornar_lista_vazia_quando_banco_estiver_limpo(mock_supabase):
    # Arrange
    # Simula o banco respondendo sem erros estruturais, mas sem nenhuma linha cadastrada
    mock_execute = MagicMock()
    mock_execute.data = []  
    
    # Configura o encadeamento fluente sem o .eq(), condizente com a busca global
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_execute

    # Act
    resultado = Flag_repository.buscar_todos_registros()

    # Assert
    assert isinstance(resultado, list)
    assert len(resultado) == 0  # Valida se passou exatamente pelo if not resposta.data -> return []
    
    # Inspeciona as chamadas realizadas
    mock_supabase.table.assert_called_once_with("tb_flags_register")
    mock_supabase.table.return_value.select.assert_called_once_with("*")
