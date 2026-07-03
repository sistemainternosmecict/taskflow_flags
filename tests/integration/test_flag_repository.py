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


# -------------------------------------------------------------------------
# 1. TESTE DEDICADO DE INSERÇÃO (Boa prática adicionada)
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_deve_registrar_inicio_nova_flag_com_sucesso():
    # Arrange - Usa um ID totalmente isolado para este teste específico
    id_task_exclusiva = "task-teste-insercao-exclusiva"
    dados_entrada = CreateFlag(
        tb_flags_task_id=id_task_exclusiva,
        tb_flags_task_user_id="user-teste-000"
    )

    try:
        # Act - Executa a inserção real
        resultado = Flag_repository.registrar_inicio_nova_flag(dados_entrada)

        # Assert - Valida minuciosamente o comportamento do método de escrita
        assert isinstance(resultado, FlagResponse)
        assert resultado.tb_flags_task_id == id_task_exclusiva
        assert resultado.tb_flags_status == FlagStatusEnum.ENTREGA_PARCIAL
        assert resultado.tb_flags_id is not None  # Garante a PK gerada pelo Postgres

    finally:
        # Teardown local - Limpa a sujeira gerada exclusivamente por este teste
        supabase.table("tb_flags_register").delete().eq("tb_flags_task_id", id_task_exclusiva).execute()


# -------------------------------------------------------------------------
# 2. TESTES QUE USAM A FIXTURE COMPARTILHADA (Busca e Update)
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_deve_garantir_existencia_da_flag(id_task_compartilhada):
    resultado = Flag_repository.buscar_registro_flag(id_task_compartilhada)
    assert isinstance(resultado, list)
    assert len(resultado) > 0
    assert isinstance(resultado[0], FlagResponse)
    assert resultado[0].tb_flags_task_id == id_task_compartilhada


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

    # Act & Assert - O banco real vai retornar zero linhas afetadas e o Python deve lançar o ValueError
    with pytest.raises(ValueError) as exc_info:
        Flag_repository.mudar_status_flag(payload_update)

    assert str(exc_info.value) == mensagem_esperada


# -------------------------------------------------------------------------
# 4. TESTE DE INTEGRAÇÃO: Retorno de lista vazia no buscar_registro_flag
# -------------------------------------------------------------------------
@pytest.mark.integration
def test_integracao_supabase_buscar_registro_flag_deve_retornar_lista_vazia_para_task_inexistente():
    # Arrange - Usa um ID fictício que não possui registros associados
    id_inexistente = "task-integracao-sem-dados-999"

    # Act - Executa a consulta real no Supabase
    resultado = Flag_repository.buscar_registro_flag(id_inexistente)

    # Assert - Garante que a API do banco respondeu sem erros, e o repositório devolveu uma lista puramente vazia []
    assert isinstance(resultado, list)
    assert len(resultado) == 0
