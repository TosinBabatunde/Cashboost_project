with farmers as (
    select * from {{ref ('stg_cashboost_farmers')}}
),

summary as (

    select
        treatment_group,
        region,
        farm_size,
        enrollment_cohort,

        count (distinct farmer_id) as total_farmers,

        round(avg(baseline_income_usd), 2) as avg_baseline_income,
        round(avg(endline_income_usd), 2) as avg_endline_income,
        round(avg(income_change_usd), 2) as avg_income_change,

        round(avg(baseline_food_security_score), 2) as avg_baseline_food_security,
        round(avg(endline_food_security_score), 2) as avg_endline_food_security,

        round(avg(baseline_farm_output_kg), 2) as avg_baseline_output_kg,
        round(avg(endline_farm_output_kg), 2) as avg_endline_output_kg,

        round(avg(sessions_attended), 1) as avg_sessions_attended

    from farmers
    group by 1,2,3,4

)

select * from summary