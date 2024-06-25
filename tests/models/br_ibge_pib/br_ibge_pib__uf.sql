{{ config(alias="uf", schema="br_ibge_pib") }}
select
    safe_cast(ano as int64) ano,
    safe_cast(id_uf as string) id_uf,
    safe_cast(sigla_uf as string) sigla_uf,
    safe_cast(pib as int64) pib,
    safe_cast(impostos_liquidos as int64) impostos_liquidos,
    safe_cast(va as int64) va,
    safe_cast(va_agropecuaria as int64) va_agropecuaria,
    safe_cast(va_industria as int64) va_industria,
    safe_cast(va_servicos as int64) va_servicos,
    safe_cast(va_adespss as int64) va_adespss,
from `basedosdados-dev.br_ibge_pib_staging.uf` as t
