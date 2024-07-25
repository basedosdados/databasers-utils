{{ config(alias="gini", schema="br_ibge_pib", materialized="table") }}
select
    safe_cast(id_uf as string) id_uf,
    safe_cast(ano as int64) ano,
    safe_cast(gini_pib as int64) gini_pib,
    safe_cast(gini_va as int64) gini_va,
    safe_cast(gini_va_agro as int64) gini_va_agro,
    safe_cast(gini_va_industria as int64) gini_va_industria,
    safe_cast(gini_va_servicos as int64) gini_va_servicos,
    safe_cast(gini_va_adespss as int64) gini_va_adespss,
from `basedosdados-dev.br_ibge_pib_staging.gini` as t
