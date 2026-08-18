import pytest
from domain.schemas import (
    CreateFlag,
    FlagResponse,
    UpdateFlagStatus,
    UpdateFlagResponse,
)
from domain.enum import FlagStatusEnum
from repository.flag_repository import Flag_repository, supabase

# -------------------------------------------------------------------------
# FIXTURE PARA COMPARTILHAR ESTADO NOS TESTES DE BUSCA E UPDATE
# -------------------------------------------------------------------------
@pytest.fixture(scope="module")
def id_task_compartilhada():
    id_teste = "task-teste-integracao-999"
    dados_entrada = CreateFlag(
        tb_flags_task_id=id_teste,
        tb_flags_task_user_id="user-teste-123"
    )
    Flag_repository.registrar_inicio_nova_flag(dados_entrada)
    yield id_teste
    supabase.table("tb_flags_register").delete().eq("tb_flags_task_id", id_teste).execute()

@pytest.mark.integration
def test_integracao_supabase_buscar_todos_registros_deve_retornar_lista_de_flag_response_com_sucesso(id_task_compartilhada):
    resultado = Flag_repository.buscar_todos_registros()
    assert isinstance(resultado, list)
    assert len(resultado) > 0  # Garante que a lista não veio vazia

    flag_criada_na_fixture = next(
        (f for f in resultado if f.tb_flags_task_id == id_task_compartilhada), 
        None
    )

    assert flag_criada_na_fixture is not None, f"A flag com id {id_task_compartilhada} deveria estar na listagem"
    assert isinstance(flag_criada_na_fixture, FlagResponse)
    assert flag_criada_na_fixture.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
    assert flag_criada_na_fixture.tb_flags_id is not None  # PK gerada pelo banco

# -------------------------------------------------------------------------
# 1. TESTE DEDICADO DE INSERÇÃO (Boa prática adicionada)
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_deve_registrar_inicio_nova_flag_com_sucesso():
    id_task_exclusiva = "task-teste-insercao-exclusiva"
    dados_entrada = CreateFlag(
        tb_flags_task_id=id_task_exclusiva,
        tb_flags_task_user_id="user-teste-000"
    )

    try:
        resultado = Flag_repository.registrar_inicio_nova_flag(dados_entrada)
        assert isinstance(resultado, FlagResponse)
        assert resultado.tb_flags_task_id == id_task_exclusiva
        assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
        assert resultado.tb_flags_id is not None  # Garante a PK gerada pelo Postgres

    finally:
        supabase.table("tb_flags_register").delete().eq("tb_flags_task_id", id_task_exclusiva).execute()


# -------------------------------------------------------------------------
# 2. TESTES QUE USAM A FIXTURE COMPARTILHADA (Busca e Update)
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_deve_garantir_existencia_da_flag(id_task_compartilhada):
    resultado = Flag_repository.buscar_registro_flag(id_task_compartilhada)
    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_task_id == id_task_compartilhada


@pytest.mark.integration
def test_integracao_supabase_mudar_status_flag_real(id_task_compartilhada):
    payload_update = UpdateFlagStatus(
        tb_flags_task_id=id_task_compartilhada,
        tb_flags_status=FlagStatusEnum.FALTA_EQUIPAMENTO
    )

    resultado = Flag_repository.mudar_status_flag(payload_update)

    assert isinstance(resultado, UpdateFlagResponse)
    assert resultado.tb_flags_status == FlagStatusEnum.FALTA_EQUIPAMENTO
    assert resultado.tb_updated_at is not None

# -------------------------------------------------------------------------
# 3. TESTE DE INTEGRAÇÃO: raise ValueError no mudar_status_flag
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_mudar_status_flag_deve_lancar_value_error_para_task_inexistente():
    # Arrange - Cria um ID fictício que garantidamente não existe no seu banco real
    id_inexistente = "task-integracao-inexistente-404"
    payload_update = UpdateFlagStatus(
        tb_flags_task_id=id_inexistente,
        tb_flags_status=FlagStatusEnum.FALTA_EQUIPAMENTO
    )

    mensagem_esperada = f"Nenhuma flag encontrada para a task {id_inexistente}"
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.mudar_status_flag(payload_update)

    assert str(exc_info.value) == mensagem_esperada


# -------------------------------------------------------------------------
# 4. TESTE DE INTEGRAÇÃO: Retorno de lista vazia no buscar_registro_flag
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_buscar_registro_flag_deve_retornar_lista_vazia_para_task_inexistente():
    id_inexistente = "task-integracao-sem-dados-999"
    resultado = Flag_repository.buscar_registro_flag(id_inexistente)

    assert isinstance(resultado, list)
    assert len(resultado) == 0

@pytest.mark.integration
def test_integracao_supabase_buscar_todos_registros_deve_retornar_lista_vazia_quando_tabela_nao_tiver_dados():
    supabase.table("tb_flags_register").delete().neq("tb_flags_task_id", "forcar_delete_de_tudo").execute()

    try:
        resultado = Flag_repository.buscar_todos_registros()
        assert isinstance(resultado, list)
        assert len(resultado) == 0  # Garante que bateu no banco real e retornou zero registros

    finally:
        pass


# -------------------------------------------------------------------------
# 5. TESTES DE INTEGRAÇÃO: remover_flag
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_remover_flag_com_sucesso():
    id_task_delete = "task-teste-remocao-exclusiva"
    dados_entrada = CreateFlag(
        tb_flags_task_id=id_task_delete,
        tb_flags_task_user_id="user-teste-remocao",
    )
    Flag_repository.registrar_inicio_nova_flag(dados_entrada)

    resultado = Flag_repository.remover_flag(id_task_delete)

    assert isinstance(resultado, FlagResponse)
    assert resultado.tb_flags_task_id == id_task_delete

    # Confirma que o registro foi realmente deletado do banco
    consulta_pos_delete = Flag_repository.buscar_registro_flag(id_task_delete)
    assert consulta_pos_delete == []


@pytest.mark.integration
def test_integracao_supabase_remover_flag_deve_lancar_value_error_para_task_inexistente():
    id_inexistente = "task-integracao-inexistente-delete-404"

    mensagem_esperada = f"Nenhuma flag encontrada para a task {id_inexistente}"
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.remover_flag(id_inexistente)

    assert str(exc_info.value) == mensagem_esperada


# -------------------------------------------------------------------------
# 6. TESTES DE INTEGRAÇÃO: buscar_flags_por_task_ids
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_buscar_flags_por_task_ids():
    id_task_batch = "task-teste-batch-001"
    dados_entrada = CreateFlag(
        tb_flags_task_id=id_task_batch,
        tb_flags_task_user_id="user-teste-batch",
    )
    Flag_repository.registrar_inicio_nova_flag(dados_entrada)

    try:
        resultado = Flag_repository.buscar_flags_por_task_ids([id_task_batch, "task-inexistente-xyz"])
        assert isinstance(resultado, list)
        assert len(resultado) == 1
        assert resultado[0].tb_flags_task_id == id_task_batch
    finally:
        supabase.table("tb_flags_register").delete().eq("tb_flags_task_id", id_task_batch).execute()


@pytest.mark.integration
def test_integracao_supabase_buscar_flags_por_task_ids_vazio():
    resultado = Flag_repository.buscar_flags_por_task_ids([])
    assert resultado == []


@pytest.mark.integration
def test_integracao_supabase_buscar_flags_por_task_ids_inexistentes_retorna_lista_vazia():
    resultado = Flag_repository.buscar_flags_por_task_ids(["task-inexistente-batch-999"])
    assert isinstance(resultado, list)
    assert len(resultado) == 0



