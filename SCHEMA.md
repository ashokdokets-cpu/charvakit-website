# Charvak Database Schema

**Generated:** 2026-10-03
**Total tables:** 164

**Purpose:** Complete snapshot of every `charvak_*` table.
Re-generate with: `python scripts/regenerate_schema.py`

---

## Table Index

- [charvak_advanced_ai_sessions](#charvak-advanced-ai-sessions)
- [charvak_advanced_mock_drives](#charvak-advanced-mock-drives)
- [charvak_advanced_skill_gaps](#charvak-advanced-skill-gaps)
- [charvak_ai_bridge_premium_reports](#charvak-ai-bridge-premium-reports)
- [charvak_ai_bridge_sessions](#charvak-ai-bridge-sessions)
- [charvak_ai_internship_custom_programs](#charvak-ai-internship-custom-programs)
- [charvak_ai_internship_enrollments](#charvak-ai-internship-enrollments)
- [charvak_ai_internship_scenarios](#charvak-ai-internship-scenarios)
- [charvak_ai_internship_submissions](#charvak-ai-internship-submissions)
- [charvak_ai_internship_tiers](#charvak-ai-internship-tiers)
- [charvak_aiqg_daily_usage](#charvak-aiqg-daily-usage)
- [charvak_aiqg_question_cache](#charvak-aiqg-question-cache)
- [charvak_alumni_connections](#charvak-alumni-connections)
- [charvak_applications](#charvak-applications)
- [charvak_assessment_reports](#charvak-assessment-reports)
- [charvak_assessment_results](#charvak-assessment-results)
- [charvak_ats_integrations](#charvak-ats-integrations)
- [charvak_ats_sync_log](#charvak-ats-sync-log)
- [charvak_auditbot_fixes](#charvak-auditbot-fixes)
- [charvak_auditbot_subscriptions](#charvak-auditbot-subscriptions)
- [charvak_auth_tokens](#charvak-auth-tokens)
- [charvak_badges](#charvak-badges)
- [charvak_booking_requests](#charvak-booking-requests)
- [charvak_brand_promoted_jobs](#charvak-brand-promoted-jobs)
- [charvak_brand_reviews](#charvak-brand-reviews)
- [charvak_brands](#charvak-brands)
- [charvak_bridge_premium_reports](#charvak-bridge-premium-reports)
- [charvak_bridge_sessions](#charvak-bridge-sessions)
- [charvak_candidates](#charvak-candidates)
- [charvak_career_assessment_answers](#charvak-career-assessment-answers)
- [charvak_career_assessments](#charvak-career-assessments)
- [charvak_career_company_follows](#charvak-career-company-follows)
- [charvak_career_interviews](#charvak-career-interviews)
- [charvak_career_job_alerts](#charvak-career-job-alerts)
- [charvak_career_offers](#charvak-career-offers)
- [charvak_career_salary_reports](#charvak-career-salary-reports)
- [charvak_career_saved_jobs](#charvak-career-saved-jobs)
- [charvak_cbat_answers](#charvak-cbat-answers)
- [charvak_cbat_sessions](#charvak-cbat-sessions)
- [charvak_certificates](#charvak-certificates)
- [charvak_chatbot_sessions](#charvak-chatbot-sessions)
- [charvak_company_content_progress](#charvak-company-content-progress)
- [charvak_content_used_content](#charvak-content-used-content)
- [charvak_course_installments](#charvak-course-installments)
- [charvak_course_lessons](#charvak-course-lessons)
- [charvak_course_payments](#charvak-course-payments)
- [charvak_course_prices](#charvak-course-prices)
- [charvak_courses](#charvak-courses)
- [charvak_credit_purchases](#charvak-credit-purchases)
- [charvak_credit_usage_history](#charvak-credit-usage-history)
- [charvak_doketsrb_bundle_subs](#charvak-doketsrb-bundle-subs)
- [charvak_doketsrb_score_events](#charvak-doketsrb-score-events)
- [charvak_doketsrb_score_tokens](#charvak-doketsrb-score-tokens)
- [charvak_dynamic_custom_roles](#charvak-dynamic-custom-roles)
- [charvak_dynamic_role_profiles](#charvak-dynamic-role-profiles)
- [charvak_enrollments](#charvak-enrollments)
- [charvak_enterprise_appointments](#charvak-enterprise-appointments)
- [charvak_enterprise_employer_tiers](#charvak-enterprise-employer-tiers)
- [charvak_enterprise_kiosk_events](#charvak-enterprise-kiosk-events)
- [charvak_enterprise_kiosk_sessions](#charvak-enterprise-kiosk-sessions)
- [charvak_enterprise_pathways](#charvak-enterprise-pathways)
- [charvak_enterprise_resume_approvals](#charvak-enterprise-resume-approvals)
- [charvak_enterprise_resume_books](#charvak-enterprise-resume-books)
- [charvak_enterprise_salary_data](#charvak-enterprise-salary-data)
- [charvak_enterprise_surveys](#charvak-enterprise-surveys)
- [charvak_escrow_transactions](#charvak-escrow-transactions)
- [charvak_event_rsvps](#charvak-event-rsvps)
- [charvak_events](#charvak-events)
- [charvak_exam_analytics_history](#charvak-exam-analytics-history)
- [charvak_exam_analytics_performance](#charvak-exam-analytics-performance)
- [charvak_exam_mock_tests](#charvak-exam-mock-tests)
- [charvak_exam_question_bank](#charvak-exam-question-bank)
- [charvak_exam_study_plans](#charvak-exam-study-plans)
- [charvak_exam_test_answers](#charvak-exam-test-answers)
- [charvak_exam_user_progress](#charvak-exam-user-progress)
- [charvak_feature_interest](#charvak-feature-interest)
- [charvak_fyp_subscriptions](#charvak-fyp-subscriptions)
- [charvak_geo_compliance_contracts](#charvak-geo-compliance-contracts)
- [charvak_geo_compliance_hiring](#charvak-geo-compliance-hiring)
- [charvak_interview_answers](#charvak-interview-answers)
- [charvak_interview_sessions](#charvak-interview-sessions)
- [charvak_jobs](#charvak-jobs)
- [charvak_kyc_partners](#charvak-kyc-partners)
- [charvak_kyc_verifications](#charvak-kyc-verifications)
- [charvak_kyc_verified_users](#charvak-kyc-verified-users)
- [charvak_lang_ai_assessments](#charvak-lang-ai-assessments)
- [charvak_lang_ai_submissions](#charvak-lang-ai-submissions)
- [charvak_legacy_shift_reports](#charvak-legacy-shift-reports)
- [charvak_lms_certificates](#charvak-lms-certificates)
- [charvak_lms_discussions](#charvak-lms-discussions)
- [charvak_lms_enrollments](#charvak-lms-enrollments)
- [charvak_lms_lesson_progress](#charvak-lms-lesson-progress)
- [charvak_lms_lessons](#charvak-lms-lessons)
- [charvak_lms_payouts](#charvak-lms-payouts)
- [charvak_lms_quiz_attempts](#charvak-lms-quiz-attempts)
- [charvak_lms_quizzes](#charvak-lms-quizzes)
- [charvak_lms_ratings](#charvak-lms-ratings)
- [charvak_lock_in_engagements](#charvak-lock-in-engagements)
- [charvak_marketing_booking_kits](#charvak-marketing-booking-kits)
- [charvak_marketing_job_ads](#charvak-marketing-job-ads)
- [charvak_marketing_lead_drips](#charvak-marketing-lead-drips)
- [charvak_marketing_social_posts](#charvak-marketing-social-posts)
- [charvak_master_profiles](#charvak-master-profiles)
- [charvak_messages](#charvak-messages)
- [charvak_micro_applications](#charvak-micro-applications)
- [charvak_micro_clients](#charvak-micro-clients)
- [charvak_micro_projects](#charvak-micro-projects)
- [charvak_micro_squad_leads](#charvak-micro-squad-leads)
- [charvak_mock_answers](#charvak-mock-answers)
- [charvak_mock_sessions](#charvak-mock-sessions)
- [charvak_monitor_alert_history](#charvak-monitor-alert-history)
- [charvak_monitor_sites](#charvak-monitor-sites)
- [charvak_na_compliance_reports](#charvak-na-compliance-reports)
- [charvak_na_cvms_requisitions](#charvak-na-cvms-requisitions)
- [charvak_na_cvms_sow_contracts](#charvak-na-cvms-sow-contracts)
- [charvak_na_cvms_timecards](#charvak-na-cvms-timecards)
- [charvak_na_match_history](#charvak-na-match-history)
- [charvak_na_redaction_log](#charvak-na-redaction-log)
- [charvak_na_revenue_subscriptions](#charvak-na-revenue-subscriptions)
- [charvak_na_revenue_transactions](#charvak-na-revenue-transactions)
- [charvak_na_sub_vendor_submissions](#charvak-na-sub-vendor-submissions)
- [charvak_na_sub_vendors](#charvak-na-sub-vendors)
- [charvak_na_verified_candidates](#charvak-na-verified-candidates)
- [charvak_na_vms_jobs](#charvak-na-vms-jobs)
- [charvak_na_vms_submissions](#charvak-na-vms-submissions)
- [charvak_network_tracker](#charvak-network-tracker)
- [charvak_notifications](#charvak-notifications)
- [charvak_outreach_auto_tracked](#charvak-outreach-auto-tracked)
- [charvak_outreach_cold_emails](#charvak-outreach-cold-emails)
- [charvak_outreach_email_syncs](#charvak-outreach-email-syncs)
- [charvak_outreach_premium_users](#charvak-outreach-premium-users)
- [charvak_payment_log](#charvak-payment-log)
- [charvak_product_results](#charvak-product-results)
- [charvak_referral_bounties](#charvak-referral-bounties)
- [charvak_referral_clicks](#charvak-referral-clicks)
- [charvak_referrals](#charvak-referrals)
- [charvak_reverse_staffing_subscriptions](#charvak-reverse-staffing-subscriptions)
- [charvak_role_manager_custom_roles](#charvak-role-manager-custom-roles)
- [charvak_silent_killer_scans](#charvak-silent-killer-scans)
- [charvak_silent_killer_watches](#charvak-silent-killer-watches)
- [charvak_skill_gaps](#charvak-skill-gaps)
- [charvak_skill_twin_results](#charvak-skill-twin-results)
- [charvak_student_suite_subscriptions](#charvak-student-suite-subscriptions)
- [charvak_student_suite_usage](#charvak-student-suite-usage)
- [charvak_synced_applications](#charvak-synced-applications)
- [charvak_synced_users](#charvak-synced-users)
- [charvak_team_members](#charvak-team-members)
- [charvak_team_subscriptions](#charvak-team-subscriptions)
- [charvak_teams](#charvak-teams)
- [charvak_tool_results](#charvak-tool-results)
- [charvak_training_courses](#charvak-training-courses)
- [charvak_training_enrollments](#charvak-training-enrollments)
- [charvak_training_plans](#charvak-training-plans)
- [charvak_universities](#charvak-universities)
- [charvak_university_outcomes](#charvak-university-outcomes)
- [charvak_university_students](#charvak-university-students)
- [charvak_university_subscriptions](#charvak-university-subscriptions)
- [charvak_user_ability](#charvak-user-ability)
- [charvak_user_credits](#charvak-user-credits)
- [charvak_voice_to_web_domains](#charvak-voice-to-web-domains)
- [charvak_voice_to_web_seo](#charvak-voice-to-web-seo)
- [charvak_voice_to_web_sites](#charvak-voice-to-web-sites)
- [charvak_voice_to_web_tickets](#charvak-voice-to-web-tickets)
- [charvak_voice_to_web_updates](#charvak-voice-to-web-updates)

---

## charvak_advanced_ai_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_advanced_ai_sessions_pkey`
- `idx_adv_sessions_started`

---

## charvak_advanced_mock_drives

| Column | Type | Nullable | Default |
|---|---|---|---|
| drive_id | text | NO |  |
| email | text | YES |  |
| company | text | YES |  |
| data | jsonb | NO | '{}'::jsonb |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_advanced_mock_drives_pkey`
- `idx_adv_drives_company`
- `idx_adv_drives_email`

---

## charvak_advanced_skill_gaps

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| analyzed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_advanced_skill_gaps_pkey`
- `idx_adv_skill_gaps_analyzed`

---

## charvak_ai_bridge_premium_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| premium_id | text | NO |  |
| session_id | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| price | integer | YES | 99 |
| purchased_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_bridge_premium_reports_pkey`
- `idx_aib_premium_session`

---

## charvak_ai_bridge_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_bridge_sessions_pkey`
- `idx_aib_sessions_started`

---

## charvak_ai_internship_custom_programs

| Column | Type | Nullable | Default |
|---|---|---|---|
| program_id | text | NO |  |
| name | text | NO |  |
| role_title | text | NO |  |
| category | text | YES | 'Custom'::text |
| skills | jsonb | YES | '[]'::jsonb |
| deliverables | jsonb | YES | '[]'::jsonb |
| outline | jsonb | YES | '[]'::jsonb |
| max_days | integer | YES | 80 |
| requested_by | text | YES |  |
| is_public | integer | YES | 1 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_internship_custom_programs_pkey`

---

## charvak_ai_internship_enrollments

| Column | Type | Nullable | Default |
|---|---|---|---|
| enrollment_id | text | NO |  |
| email | text | NO |  |
| program_id | text | NO |  |
| duration | text | YES | 'standard'::text |
| total_days | integer | YES | 28 |
| current_day | integer | YES | 1 |
| status | text | NO | 'active'::text |
| start_date | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |
| tier_key | text | YES | 'standard'::text |
| mentor_asks_used | integer | YES | 0 |
| amount_paid_inr | integer | YES | 0 |
| razorpay_payment_id | text | YES |  |

**Indexes:**

- `charvak_ai_internship_enrollments_pkey`
- `idx_ai_intern_email`
- `idx_ai_intern_program`
- `idx_ai_intern_status`

---

## charvak_ai_internship_scenarios

| Column | Type | Nullable | Default |
|---|---|---|---|
| scenario_id | text | NO |  |
| program_id | text | NO |  |
| tier_key | text | NO |  |
| day | integer | NO |  |
| role_title | text | NO |  |
| title | text | NO |  |
| overview | text | NO |  |
| learning_objectives | jsonb | YES | '[]'::jsonb |
| step_by_step | jsonb | YES | '[]'::jsonb |
| deliverable | text | YES |  |
| acceptance_criteria | jsonb | YES | '[]'::jsonb |
| resources | jsonb | YES | '[]'::jsonb |
| mentor_note | text | YES |  |
| estimated_time | text | YES |  |
| difficulty | text | YES |  |
| raw_json | jsonb | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_internship_scenarios_pkey`
- `charvak_ai_internship_scenarios_program_id_tier_key_day_key`
- `idx_ai_intern_scen_lookup`

---

## charvak_ai_internship_submissions

| Column | Type | Nullable | Default |
|---|---|---|---|
| submission_id | text | NO |  |
| enrollment_id | text | NO |  |
| day | integer | NO |  |
| submission | text | YES |  |
| ai_feedback | jsonb | YES | '{}'::jsonb |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_internship_submissions_enrollment_id_day_key`
- `charvak_ai_internship_submissions_pkey`
- `idx_ai_intern_sub_enroll`

---

## charvak_ai_internship_tiers

| Column | Type | Nullable | Default |
|---|---|---|---|
| tier_key | text | NO |  |
| tier_name | text | NO |  |
| weeks | integer | NO |  |
| business_days | integer | NO |  |
| price_inr | integer | NO |  |
| price_usd | integer | NO |  |
| display_order | integer | NO |  |
| is_active | integer | YES | 1 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ai_internship_tiers_pkey`

---

## charvak_aiqg_daily_usage

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| usage_date | date | NO |  |
| count | integer | YES | 0 |

**Indexes:**

- `charvak_aiqg_daily_usage_pkey`
- `idx_aiqg_usage_date`

---

## charvak_aiqg_question_cache

| Column | Type | Nullable | Default |
|---|---|---|---|
| cache_key | text | NO |  |
| questions | jsonb | NO | '[]'::jsonb |
| timestamp | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_aiqg_question_cache_pkey`
- `idx_aiqg_cache_ts`

---

## charvak_alumni_connections

| Column | Type | Nullable | Default |
|---|---|---|---|
| connection_id | text | NO |  |
| university | text | YES |  |
| name | text | YES |  |
| email | text | YES |  |
| company | text | YES |  |
| role | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_alumni_connections_pkey`
- `idx_alumni_company`
- `idx_alumni_email`
- `idx_alumni_university`

---

## charvak_applications

| Column | Type | Nullable | Default |
|---|---|---|---|
| application_id | text | NO |  |
| job_id | text | NO |  |
| user_id | text | YES | 'anonymous'::text |
| resume_url | text | YES | ''::text |
| applied_at | text | YES | ''::text |
| status | text | YES | 'applied'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_applications_pkey`

---

## charvak_assessment_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| report_id | text | NO |  |
| verification_id | text | NO |  |
| assessment_type | text | YES | 'general'::text |
| candidate_name | text | YES |  |
| candidate_email | text | YES |  |
| employer_email | text | YES | ''::text |
| score | numeric | YES | 0 |
| passed | boolean | YES | false |
| skills_tested | jsonb | YES | '[]'::jsonb |
| total_questions | integer | YES | 0 |
| correct_answers | integer | YES | 0 |
| strengths | jsonb | YES | '[]'::jsonb |
| improvements | jsonb | YES | '[]'::jsonb |
| recommendations | jsonb | YES | '[]'::jsonb |
| generated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_assessment_reports_pkey`
- `charvak_assessment_reports_verification_id_key`
- `idx_asr_candidate_email`
- `idx_asr_passed`
- `idx_asr_verification`

---

## charvak_assessment_results

| Column | Type | Nullable | Default |
|---|---|---|---|
| result_id | text | NO |  |
| email | text | NO |  |
| assessment_type | text | NO |  |
| assessment_name | text | NO |  |
| score | numeric | NO |  |
| total_questions | integer | NO |  |
| correct_answers | integer | NO |  |
| percentage | numeric | NO |  |
| passed | boolean | NO |  |
| details_json | jsonb | YES |  |
| completed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_assessment_results_pkey`
- `idx_assessment_results_completed`
- `idx_assessment_results_email`
- `idx_assessment_results_type`

---

## charvak_ats_integrations

| Column | Type | Nullable | Default |
|---|---|---|---|
| integration_id | text | NO |  |
| provider | text | YES |  |
| api_key_prefix | text | YES |  |
| base_url | text | YES | ''::text |
| company_name | text | YES |  |
| direction | text | YES | 'bidirectional'::text |
| status | text | YES | 'connected'::text |
| connected_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ats_integrations_pkey`
- `idx_ats_integrations_provider`
- `idx_ats_integrations_status`

---

## charvak_ats_sync_log

| Column | Type | Nullable | Default |
|---|---|---|---|
| sync_id | text | NO |  |
| direction | text | YES |  |
| provider | text | YES |  |
| jobs_count | integer | YES | 0 |
| details | jsonb | NO | '{}'::jsonb |
| synced_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_ats_sync_log_pkey`
- `idx_ats_sync_direction`
- `idx_ats_sync_provider`

---

## charvak_auditbot_fixes

| Column | Type | Nullable | Default |
|---|---|---|---|
| fix_id | text | NO |  |
| email | text | NO |  |
| scan_id | text | YES |  |
| repo_url | text | YES |  |
| language | text | YES |  |
| scan_type | text | YES |  |
| findings_json | jsonb | YES |  |
| guide_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_auditbot_fixes_pkey`
- `idx_auditbot_fixes_email`
- `idx_auditbot_fixes_scan`

---

## charvak_auditbot_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| tier | text | NO | 'continuous'::text |
| started_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |
| scans_used | integer | NO | 0 |
| last_scan_at | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_auditbot_subscriptions_pkey`
- `idx_auditbot_subs_expires`

---

## charvak_auth_tokens

| Column | Type | Nullable | Default |
|---|---|---|---|
| token | text | NO |  |
| user_id | text | YES |  |
| email | text | NO |  |
| role | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |

**Indexes:**

- `charvak_auth_tokens_pkey`
- `idx_charvak_auth_tokens_email`
- `idx_charvak_auth_tokens_expires`

---

## charvak_badges

| Column | Type | Nullable | Default |
|---|---|---|---|
| badge_id | text | NO |  |
| badge_name | text | YES |  |
| level | text | YES |  |
| color | text | YES | '#3ba591'::text |
| user_name | text | YES |  |
| user_email | text | NO |  |
| score | integer | YES |  |
| skills | jsonb | YES | '[]'::jsonb |
| badge_type | text | YES |  |
| issued_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| valid_until | timestamp without time zone | YES |  |
| verification_hash | text | YES |  |
| share_url | text | YES |  |
| linkedin_url | text | YES |  |

**Indexes:**

- `charvak_badges_pkey`
- `idx_badges_level`
- `idx_badges_type`
- `idx_badges_user_email`
- `idx_badges_valid`

---

## charvak_booking_requests

| Column | Type | Nullable | Default |
|---|---|---|---|
| request_id | text | NO |  |
| slug | text | NO |  |
| kit_id | text | NO |  |
| host_email | text | NO |  |
| prospect_name | text | NO |  |
| prospect_email | text | NO |  |
| preferred_time | text | YES |  |
| notes | text | YES |  |
| status | text | NO | 'pending'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_booking_requests_pkey`

---

## charvak_brand_promoted_jobs

| Column | Type | Nullable | Default |
|---|---|---|---|
| promotion_id | text | NO |  |
| job_id | text | YES |  |
| company_id | text | YES |  |
| starts_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| ends_at | timestamp without time zone | YES |  |
| views | integer | YES | 0 |
| clicks | integer | YES | 0 |

**Indexes:**

- `charvak_brand_promoted_jobs_pkey`
- `idx_brand_promos_company`
- `idx_brand_promos_job`

---

## charvak_brand_reviews

| Column | Type | Nullable | Default |
|---|---|---|---|
| review_id | text | NO |  |
| company_id | text | NO |  |
| reviewer_name | text | YES |  |
| reviewer_type | text | YES | 'candidate'::text |
| rating | integer | YES | 5 |
| title | text | YES | ''::text |
| review | text | YES | ''::text |
| would_recommend | boolean | YES | true |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_brand_reviews_pkey`
- `idx_brand_reviews_company`
- `idx_brand_reviews_rating`

---

## charvak_brands

| Column | Type | Nullable | Default |
|---|---|---|---|
| brand_id | text | NO |  |
| company_name | text | YES |  |
| industry | text | YES | ''::text |
| description | text | YES | ''::text |
| logo_url | text | YES | ''::text |
| website | text | YES | ''::text |
| location | text | YES | ''::text |
| size | text | YES | ''::text |
| culture_tags | jsonb | YES | '[]'::jsonb |
| average_rating | numeric | YES | 0 |
| review_count | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_brands_pkey`
- `idx_brands_company`
- `idx_brands_industry`

---

## charvak_bridge_premium_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| report_id | text | NO |  |
| email | text | NO |  |
| students | integer | YES |  |
| placement_rate | numeric | YES |  |
| avg_salary | numeric | YES |  |
| isa_percent | numeric | YES |  |
| isa_months | integer | YES |  |
| report_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_bridge_premium_reports_pkey`

---

## charvak_bridge_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| current_step | integer | YES | 1 |
| answers | jsonb | YES | '{}'::jsonb |
| scores | jsonb | YES | '{}'::jsonb |
| readiness | integer | YES | 0 |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_bridge_sessions_pkey`
- `idx_bridge_started`

---

## charvak_candidates

| Column | Type | Nullable | Default |
|---|---|---|---|
| candidate_id | text | NO |  |
| name | text | NO |  |
| email | text | NO |  |
| phone | text | YES | ''::text |
| skills | jsonb | YES | '[]'::jsonb |
| experience_years | integer | YES | 0 |
| years_coding | integer | YES |  |
| job_title | text | YES | ''::text |
| preferred_roles | jsonb | YES | '[]'::jsonb |
| location | text | YES | ''::text |
| visa_status | text | YES | ''::text |
| portfolio_url | text | YES | ''::text |
| github_url | text | YES | ''::text |
| linkedin_url | text | YES | ''::text |
| resume_text | text | YES | ''::text |
| education | text | YES | ''::text |
| degree | text | YES | ''::text |
| major | text | YES | ''::text |
| university | text | YES | ''::text |
| gpa | numeric | YES |  |
| graduation_year | integer | YES |  |
| certifications | jsonb | YES | '[]'::jsonb |
| languages_spoken | jsonb | YES | '[]'::jsonb |
| work_authorization | text | YES | ''::text |
| willing_to_relocate | boolean | YES | false |
| remote_preference | text | YES | 'Open'::text |
| salary_expectation | text | YES | ''::text |
| availability | text | YES | 'Immediate'::text |
| status | text | YES | 'registered'::text |
| skill_score | integer | YES |  |
| badge_id | text | YES |  |
| placement | jsonb | YES |  |
| registered_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_candidates_email_key`
- `charvak_candidates_pkey`
- `idx_candidates_email`
- `idx_candidates_experience`
- `idx_candidates_grad_year`
- `idx_candidates_location`
- `idx_candidates_skill_score`
- `idx_candidates_skills_gin`
- `idx_candidates_status`
- `idx_candidates_university`
- `idx_candidates_visa`

---

## charvak_career_assessment_answers

| Column | Type | Nullable | Default |
|---|---|---|---|
| answer_id | text | NO |  |
| assessment_id | text | NO |  |
| question_index | integer | NO |  |
| selected_index | integer | YES |  |
| is_correct | boolean | YES |  |
| answered_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| answer_text | text | YES |  |
| ai_score | integer | YES |  |
| ai_feedback | text | YES |  |

**Indexes:**

- `charvak_career_assessment_answ_assessment_id_question_index_key`
- `charvak_career_assessment_answers_pkey`
- `idx_career_answers_assess`

---

## charvak_career_assessments

| Column | Type | Nullable | Default |
|---|---|---|---|
| assessment_id | text | NO |  |
| email | text | NO |  |
| role | text | NO |  |
| industry | text | NO |  |
| level | text | NO |  |
| format | text | NO | 'mcq'::text |
| size | text | NO | 'quick'::text |
| num_questions | integer | NO | 10 |
| questions_json | jsonb | NO | '[]'::jsonb |
| status | text | NO | 'in_progress'::text |
| score | integer | YES |  |
| passed | boolean | YES |  |
| correct_count | integer | YES |  |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |
| learning_path_json | jsonb | YES |  |

**Indexes:**

- `charvak_career_assessments_pkey`
- `idx_career_assess_email`
- `idx_career_assess_status`

---

## charvak_career_company_follows

| Column | Type | Nullable | Default |
|---|---|---|---|
| follow_id | text | NO |  |
| email | text | NO |  |
| company | text | NO |  |
| followed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_company_follows_email_company_key`
- `charvak_career_company_follows_pkey`
- `idx_career_follows_email`

---

## charvak_career_interviews

| Column | Type | Nullable | Default |
|---|---|---|---|
| interview_id | text | NO |  |
| candidate_email | text | NO |  |
| employer | text | YES |  |
| role | text | YES |  |
| date | text | YES |  |
| platform | text | YES | 'Zoom'::text |
| status | text | YES | 'scheduled'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_interviews_pkey`
- `idx_career_interviews_email`

---

## charvak_career_job_alerts

| Column | Type | Nullable | Default |
|---|---|---|---|
| alert_id | text | NO |  |
| email | text | NO |  |
| keywords | jsonb | YES | '[]'::jsonb |
| location | text | YES | ''::text |
| frequency | text | YES | 'daily'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_job_alerts_pkey`
- `idx_career_alerts_email`

---

## charvak_career_offers

| Column | Type | Nullable | Default |
|---|---|---|---|
| offer_id | text | NO |  |
| candidate_email | text | NO |  |
| company | text | YES |  |
| role | text | YES |  |
| salary | numeric | YES | 0 |
| status | text | YES | 'received'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_offers_pkey`
- `idx_career_offers_email`

---

## charvak_career_salary_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| salary_id | text | NO |  |
| role | text | NO |  |
| company | text | YES | 'Anonymous'::text |
| amount | numeric | YES | 0 |
| location | text | YES | ''::text |
| recorded_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_salary_reports_pkey`
- `idx_career_salary_role`

---

## charvak_career_saved_jobs

| Column | Type | Nullable | Default |
|---|---|---|---|
| save_id | text | NO |  |
| email | text | NO |  |
| job_id | text | NO |  |
| saved_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_career_saved_jobs_email_job_id_key`
- `charvak_career_saved_jobs_pkey`
- `idx_career_saved_email`

---

## charvak_cbat_answers

| Column | Type | Nullable | Default |
|---|---|---|---|
| answer_id | text | NO |  |
| session_id | text | NO |  |
| question_index | integer | NO |  |
| selected | integer | YES |  |
| time_taken_ms | integer | YES |  |
| is_correct | boolean | YES |  |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_cbat_answers_pkey`
- `charvak_cbat_answers_session_id_question_index_key`
- `idx_cbat_answers_session`

---

## charvak_cbat_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| email | text | NO |  |
| sub_test | text | NO |  |
| sections_json | jsonb | NO |  |
| total_questions | integer | NO |  |
| total_time_ms | integer | NO |  |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |
| status | text | NO | 'in_progress'::text |
| score | numeric | YES |  |
| correct_count | integer | YES |  |
| passed | boolean | YES |  |

**Indexes:**

- `charvak_cbat_sessions_pkey`
- `idx_cbat_sessions_email`
- `idx_cbat_sessions_sub_test`

---

## charvak_certificates

| Column | Type | Nullable | Default |
|---|---|---|---|
| certificate_id | text | NO |  |
| enrollment_id | text | NO |  |
| email | text | NO |  |
| course_name | text | NO |  |
| duration_weeks | integer | YES |  |
| issued_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_certificates_pkey`

---

## charvak_chatbot_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_chatbot_sessions_pkey`
- `idx_chatbot_created`
- `idx_chatbot_updated`

---

## charvak_company_content_progress

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| company_id | text | NO |  |
| sections_completed | integer | YES | 0 |
| total_score | numeric | YES | 0 |
| mock_tests | integer | YES | 0 |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| last_updated | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_company_content_progress_pkey`
- `idx_ccp_company`
- `idx_ccp_email`

---

## charvak_content_used_content

| Column | Type | Nullable | Default |
|---|---|---|---|
| content_key | text | NO |  |
| used_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_content_used_content_pkey`
- `idx_content_used_at`

---

## charvak_course_installments

| Column | Type | Nullable | Default |
|---|---|---|---|
| installment_id | text | NO |  |
| enrollment_id | text | NO |  |
| email | text | NO |  |
| installment_num | integer | NO |  |
| total_installments | integer | NO |  |
| amount_inr | integer | NO |  |
| unlocks_from_week | integer | NO |  |
| unlocks_to_week | integer | NO |  |
| due_week | integer | NO |  |
| due_date | date | NO |  |
| status | text | NO | 'pending'::text |
| paid_at | timestamp without time zone | YES |  |
| payment_id | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_course_installments_enrollment_id_installment_num_key`
- `charvak_course_installments_pkey`

---

## charvak_course_lessons

| Column | Type | Nullable | Default |
|---|---|---|---|
| lesson_id | text | NO |  |
| enrollment_id | text | NO |  |
| week_num | integer | NO |  |
| topic | text | YES | ''::text |
| lesson_content | jsonb | YES |  |
| completed | boolean | YES | false |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_course_lessons_enrollment_id_week_num_key`
- `charvak_course_lessons_pkey`

---

## charvak_course_payments

| Column | Type | Nullable | Default |
|---|---|---|---|
| payment_id | text | NO |  |
| enrollment_id | text | YES |  |
| email | text | NO |  |
| course_name | text | NO |  |
| country_code | text | YES |  |
| currency | text | NO |  |
| amount_local | numeric | NO |  |
| amount_inr | integer | NO |  |
| payment_type | text | NO |  |
| installment_num | integer | YES |  |
| razorpay_payment_id | text | YES |  |
| razorpay_order_id | text | YES |  |
| paypal_order_id | text | YES |  |
| gateway | text | NO |  |
| status | text | NO | 'pending'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_course_payments_pkey`
- `charvak_course_payments_razorpay_payment_id_key`

---

## charvak_course_prices

| Column | Type | Nullable | Default |
|---|---|---|---|
| course_name | text | NO |  |
| country_code | text | NO |  |
| currency | text | NO |  |
| amount_local | numeric | NO |  |
| razorpay_paise | integer | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_course_prices_pkey`

---

## charvak_courses

| Column | Type | Nullable | Default |
|---|---|---|---|
| course_id | text | NO |  |
| course_name | text | NO |  |
| category | text | YES | 'Technology'::text |
| duration_weeks | integer | YES | 8 |
| price_inr | integer | YES | 0 |
| description | text | YES | ''::text |
| level | text | YES | 'Beginner'::text |
| icon | text | YES | ''::text |
| status | text | YES | 'active'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_courses_course_name_key`
- `charvak_courses_pkey`

---

## charvak_credit_purchases

| Column | Type | Nullable | Default |
|---|---|---|---|
| purchase_id | text | NO |  |
| email | text | NO |  |
| plan | text | NO |  |
| price | integer | NO |  |
| credits_added | integer | NO |  |
| payment_id | text | YES |  |
| status | text | NO | 'completed'::text |
| created_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_credit_purchases_payment_id_key`
- `charvak_credit_purchases_pkey`
- `idx_charvak_purchases_email`

---

## charvak_credit_usage_history

| Column | Type | Nullable | Default |
|---|---|---|---|
| usage_id | text | NO |  |
| email | text | NO |  |
| feature | text | NO |  |
| credits_used | integer | NO |  |
| created_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_credit_usage_history_pkey`
- `idx_charvak_usage_email`

---

## charvak_doketsrb_bundle_subs

| Column | Type | Nullable | Default |
|---|---|---|---|
| subscription_id | text | NO |  |
| email | text | YES |  |
| bundle | text | YES |  |
| bundle_name | text | YES |  |
| price | numeric | YES | 0 |
| includes | jsonb | YES | '[]'::jsonb |
| subscribed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_doketsrb_bundle_subs_pkey`
- `idx_doketsrb_subs_bundle`
- `idx_doketsrb_subs_email`

---

## charvak_doketsrb_score_events

| Column | Type | Nullable | Default |
|---|---|---|---|
| event_id | text | NO |  |
| candidate_id | text | NO |  |
| score | integer | YES |  |
| source | text | YES | 'doketsrb'::text |
| target_role | text | YES | ''::text |
| metadata | jsonb | YES | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_doketsrb_score_events_pkey`
- `idx_doketsrb_score_events_cand`

---

## charvak_doketsrb_score_tokens

| Column | Type | Nullable | Default |
|---|---|---|---|
| token | text | NO |  |
| candidate_id | text | NO |  |
| email | text | YES |  |
| target_role | text | YES | ''::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |
| used_at | timestamp without time zone | YES |  |
| status | text | YES | 'pending'::text |

**Indexes:**

- `charvak_doketsrb_score_tokens_pkey`
- `idx_doketsrb_score_tokens_cand`
- `idx_doketsrb_score_tokens_status`

---

## charvak_dynamic_custom_roles

| Column | Type | Nullable | Default |
|---|---|---|---|
| role_id | text | NO |  |
| name | text | NO |  |
| category | text | YES | 'Custom'::text |
| skills | jsonb | YES | '[]'::jsonb |
| tools | jsonb | YES | '[]'::jsonb |
| certifications | jsonb | YES | '[]'::jsonb |
| created_by | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_dynamic_custom_roles_pkey`
- `idx_dynrole_custom_created_by`

---

## charvak_dynamic_role_profiles

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| skills | jsonb | YES | '[]'::jsonb |
| interests | jsonb | YES | '[]'::jsonb |
| experience_level | text | YES | 'fresher'::text |
| recommendations | jsonb | YES | '[]'::jsonb |
| ai_insights | jsonb | YES | '[]'::jsonb |
| analyzed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_dynamic_role_profiles_pkey`
- `idx_dynrole_profiles_level`

---

## charvak_enrollments

| Column | Type | Nullable | Default |
|---|---|---|---|
| enrollment_id | text | NO |  |
| email | text | NO |  |
| course_name | text | NO |  |
| duration_weeks | integer | YES | 8 |
| user_level | text | YES | 'beginner'::text |
| curriculum | jsonb | YES |  |
| progress | integer | YES | 0 |
| total_weeks | integer | YES | 8 |
| status | text | YES | 'active'::text |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_enrollments_pkey`

---

## charvak_enterprise_appointments

| Column | Type | Nullable | Default |
|---|---|---|---|
| appointment_id | text | NO |  |
| student_id | text | YES |  |
| student_name | text | YES |  |
| advisor_id | text | YES |  |
| date | text | YES |  |
| duration_minutes | integer | YES | 30 |
| reason | text | YES | 'Career Counseling'::text |
| status | text | YES | 'booked'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_appointments_pkey`
- `idx_ent_appt_advisor`
- `idx_ent_appt_student`

---

## charvak_enterprise_employer_tiers

| Column | Type | Nullable | Default |
|---|---|---|---|
| tier_id | text | NO |  |
| company_name | text | YES |  |
| tier | text | YES | 'tier2'::text |
| notes | text | YES | ''::text |
| set_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_employer_tiers_pkey`
- `idx_ent_tiers_company`
- `idx_ent_tiers_tier`

---

## charvak_enterprise_kiosk_events

| Column | Type | Nullable | Default |
|---|---|---|---|
| event_id | text | NO |  |
| kiosk_id | text | NO |  |
| student_id | text | NO |  |
| checked_in_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_kiosk_events_pkey`
- `idx_kiosk_events_kiosk`
- `idx_kiosk_events_student`
- `idx_kiosk_events_time`

---

## charvak_enterprise_kiosk_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| kiosk_id | text | NO |  |
| event_id | text | YES |  |
| location | text | YES | 'Main Entrance'::text |
| status | text | YES | 'active'::text |
| check_ins | integer | YES | 0 |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_kiosk_sessions_pkey`
- `idx_ent_kiosks_event`
- `idx_ent_kiosks_status`

---

## charvak_enterprise_pathways

| Column | Type | Nullable | Default |
|---|---|---|---|
| pathway_id | text | NO |  |
| name | text | YES |  |
| description | text | YES | ''::text |
| steps | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_pathways_pkey`
- `idx_ent_pathways_name`

---

## charvak_enterprise_resume_approvals

| Column | Type | Nullable | Default |
|---|---|---|---|
| review_id | text | NO |  |
| student_id | text | YES |  |
| student_name | text | YES |  |
| resume_text | text | YES | ''::text |
| status | text | YES | 'pending'::text |
| reviewer_comments | text | YES | ''::text |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| reviewed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_enterprise_resume_approvals_pkey`
- `idx_ent_resume_status`
- `idx_ent_resume_student`

---

## charvak_enterprise_resume_books

| Column | Type | Nullable | Default |
|---|---|---|---|
| book_id | text | NO |  |
| name | text | YES |  |
| description | text | YES | ''::text |
| student_ids | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_resume_books_pkey`
- `idx_ent_books_name`

---

## charvak_enterprise_salary_data

| Column | Type | Nullable | Default |
|---|---|---|---|
| salary_id | text | NO |  |
| university | text | YES |  |
| major | text | YES | ''::text |
| industry | text | YES | ''::text |
| base_salary | numeric | YES | 0 |
| signing_bonus | numeric | YES | 0 |
| location | text | YES | ''::text |
| graduation_year | integer | YES | 2026 |
| recorded_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_salary_data_pkey`
- `idx_ent_salary_inds`
- `idx_ent_salary_loc`
- `idx_ent_salary_univ`

---

## charvak_enterprise_surveys

| Column | Type | Nullable | Default |
|---|---|---|---|
| survey_id | text | NO |  |
| title | text | YES |  |
| questions | jsonb | YES | '[]'::jsonb |
| responses | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_enterprise_surveys_pkey`
- `idx_ent_surveys_title`

---

## charvak_escrow_transactions

| Column | Type | Nullable | Default |
|---|---|---|---|
| escrow_id | text | NO |  |
| client_name | text | YES |  |
| client_email | text | YES |  |
| vendor_name | text | YES |  |
| vendor_email | text | YES |  |
| amount | numeric | NO |  |
| currency | text | YES | 'INR'::text |
| platform_fee | numeric | YES | 0 |
| vendor_payout | numeric | YES | 0 |
| description | text | YES | ''::text |
| milestones | jsonb | YES | '[]'::jsonb |
| status | text | YES | 'awaiting_deposit'::text |
| payment_method | text | YES | 'Dokets VouchAI Escrow'::text |
| payment_details | jsonb | YES |  |
| delivery_data | jsonb | YES |  |
| dispute | jsonb | YES |  |
| duration_days | integer | YES | 30 |
| payout_status | text | YES | 'not_due'::text |
| payout_method | text | YES |  |
| payout_reference | text | YES |  |
| payout_amount | numeric | YES |  |
| payout_at | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| funded_at | timestamp without time zone | YES |  |
| delivered_at | timestamp without time zone | YES |  |
| released_at | timestamp without time zone | YES |  |
| expires_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_escrow_transactions_pkey`

---

## charvak_event_rsvps

| Column | Type | Nullable | Default |
|---|---|---|---|
| rsvp_id | text | NO |  |
| event_id | text | NO |  |
| user_id | text | YES |  |
| user_name | text | YES |  |
| user_email | text | NO |  |
| user_type | text | YES | 'student'::text |
| checked_in | boolean | YES | false |
| checked_in_at | timestamp without time zone | YES |  |
| rsvp_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_event_rsvps_event_id_user_email_key`
- `charvak_event_rsvps_pkey`
- `idx_rsvps_email`
- `idx_rsvps_event_id`

---

## charvak_events

| Column | Type | Nullable | Default |
|---|---|---|---|
| event_id | text | NO |  |
| title | text | YES |  |
| description | text | YES | ''::text |
| event_type | text | YES | 'webinar'::text |
| organizer_id | text | YES |  |
| organizer_name | text | YES |  |
| date | text | YES |  |
| duration_minutes | integer | YES | 60 |
| platform | text | YES | 'zoom'::text |
| location | text | YES | ''::text |
| link | text | YES | ''::text |
| max_attendees | integer | YES | 100 |
| target_audience | text | YES | 'All'::text |
| rsvp_count | integer | YES | 0 |
| status | text | NO | 'upcoming'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_events_pkey`
- `idx_events_date`
- `idx_events_status`
- `idx_events_type`

---

## charvak_exam_analytics_history

| Column | Type | Nullable | Default |
|---|---|---|---|
| history_id | text | NO |  |
| email | text | NO |  |
| exam_id | text | NO |  |
| topic | text | NO |  |
| question_id | integer | YES |  |
| correct | boolean | YES | false |
| time_taken | integer | YES | 0 |
| recorded_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_analytics_history_pkey`
- `idx_exam_analytics_hist_date`
- `idx_exam_analytics_hist_email`

---

## charvak_exam_analytics_performance

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| exam_id | text | NO |  |
| topic | text | NO |  |
| total | integer | YES | 0 |
| correct | integer | YES | 0 |
| wrong | integer | YES | 0 |
| accuracy | numeric | YES | 0 |
| avg_time | numeric | YES | 0 |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_analytics_performance_pkey`
- `idx_exam_analytics_perf_email`

---

## charvak_exam_mock_tests

| Column | Type | Nullable | Default |
|---|---|---|---|
| test_id | text | NO |  |
| email | text | NO |  |
| exam_id | text | NO |  |
| topic | text | YES | ''::text |
| status | text | NO | 'in_progress'::text |
| total_questions | integer | YES | 0 |
| correct_count | integer | YES | 0 |
| score_pct | numeric | YES | 0 |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_exam_mock_tests_pkey`
- `idx_exam_tests_email`
- `idx_exam_tests_exam`
- `idx_exam_tests_status`

---

## charvak_exam_question_bank

| Column | Type | Nullable | Default |
|---|---|---|---|
| question_id | text | NO |  |
| exam_id | text | NO |  |
| topic | text | NO |  |
| question_text | text | NO |  |
| options | jsonb | NO | '[]'::jsonb |
| correct_index | integer | NO | 0 |
| explanation | text | YES | ''::text |
| difficulty | text | YES | 'Medium'::text |
| generated_by | text | YES | 'ai'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_question_bank_exam_id_topic_question_text_key`
- `charvak_exam_question_bank_pkey`
- `idx_exam_qb_difficulty`
- `idx_exam_qb_exam_topic`

---

## charvak_exam_study_plans

| Column | Type | Nullable | Default |
|---|---|---|---|
| plan_id | text | NO |  |
| email | text | NO |  |
| exam_id | text | NO |  |
| target_date | text | YES |  |
| daily_minutes | integer | YES | 60 |
| topics | jsonb | YES | '[]'::jsonb |
| status | text | NO | 'active'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_study_plans_pkey`
- `idx_exam_plans_email`
- `idx_exam_plans_status`

---

## charvak_exam_test_answers

| Column | Type | Nullable | Default |
|---|---|---|---|
| answer_id | text | NO |  |
| test_id | text | NO |  |
| question_id | text | NO |  |
| selected_index | integer | YES |  |
| is_correct | boolean | YES | false |
| answered_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_test_answers_pkey`
- `charvak_exam_test_answers_test_id_question_id_key`
- `idx_exam_answers_test`

---

## charvak_exam_user_progress

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| exam_id | text | NO |  |
| topic | text | NO | ''::text |
| questions_attempted | integer | YES | 0 |
| questions_correct | integer | YES | 0 |
| tests_completed | integer | YES | 0 |
| best_score_pct | numeric | YES | 0 |
| last_practiced_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_exam_user_progress_pkey`
- `idx_exam_prog_email`

---

## charvak_feature_interest

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | integer | NO | nextval('charvak_feature_interest_id_... |
| email | text | NO |  |
| feature | text | NO |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_feature_interest_email_feature_key`
- `charvak_feature_interest_pkey`
- `idx_feature_interest_email`
- `idx_feature_interest_feature`

---

## charvak_fyp_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| subscription_id | text | NO |  |
| email | text | NO |  |
| plan | text | NO | 'free'::text |
| price | integer | YES | 0 |
| status | text | NO | 'active'::text |
| subscribed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_fyp_subscriptions_pkey`
- `idx_fyp_subs_email`
- `idx_fyp_subs_plan`
- `idx_fyp_subs_status`

---

## charvak_geo_compliance_contracts

| Column | Type | Nullable | Default |
|---|---|---|---|
| contract_id | text | NO |  |
| email | text | NO |  |
| countries_json | jsonb | YES |  |
| service_type | text | YES |  |
| contract_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_geo_compliance_contracts_pkey`

---

## charvak_geo_compliance_hiring

| Column | Type | Nullable | Default |
|---|---|---|---|
| setup_id | text | NO |  |
| email | text | NO |  |
| countries_json | jsonb | YES |  |
| setup_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_geo_compliance_hiring_pkey`

---

## charvak_interview_answers

| Column | Type | Nullable | Default |
|---|---|---|---|
| answer_id | text | NO |  |
| session_id | text | NO |  |
| question_num | integer | NO |  |
| question_text | text | NO |  |
| category | text | YES |  |
| user_answer | text | YES |  |
| ai_score | integer | YES |  |
| ai_feedback | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_interview_answers_pkey`

---

## charvak_interview_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| candidate_email | text | NO |  |
| role | text | NO |  |
| difficulty | text | YES | 'Intermediate'::text |
| credits_charged | integer | YES | 0 |
| total_score | integer | YES | 0 |
| max_score | integer | YES | 0 |
| questions_count | integer | YES | 0 |
| status | text | YES | 'in_progress'::text |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_interview_sessions_pkey`

---

## charvak_jobs

| Column | Type | Nullable | Default |
|---|---|---|---|
| job_id | text | NO |  |
| title | text | NO |  |
| company | text | NO |  |
| job_type | text | YES | 'Permanent'::text |
| location | text | YES | 'Remote'::text |
| salary | text | YES | ''::text |
| description | text | YES | ''::text |
| skills | text | YES | ''::text |
| posted_by | text | YES | 'api'::text |
| posted_date | text | YES | ''::text |
| status | text | YES | 'active'::text |
| applications_count | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_jobs_pkey`

---

## charvak_kyc_partners

| Column | Type | Nullable | Default |
|---|---|---|---|
| partner_id | text | NO |  |
| agency_name | text | NO |  |
| contact_person | text | YES |  |
| email | text | NO |  |
| phone | text | YES |  |
| services | jsonb | YES | '[]'::jsonb |
| coverage | text | YES | ''::text |
| status | text | NO | 'pending_review'::text |
| verifications_completed | integer | YES | 0 |
| revenue_earned | numeric | YES | 0 |
| rating | numeric | YES |  |
| registered_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| approved_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_kyc_partners_pkey`

---

## charvak_kyc_verifications

| Column | Type | Nullable | Default |
|---|---|---|---|
| verification_id | text | NO |  |
| user_name | text | YES |  |
| user_email | text | NO |  |
| user_phone | text | YES |  |
| verification_type | text | NO | 'identity'::text |
| country | text | YES | 'India'::text |
| documents_requested | jsonb | YES | '[]'::jsonb |
| documents_submitted | jsonb | YES | '[]'::jsonb |
| status | text | NO | 'pending'::text |
| price_inr | integer | YES | 499 |
| price_usd | integer | YES | 6 |
| payment_status | text | YES | 'pending'::text |
| payment_order_id | text | YES |  |
| assigned_to | text | YES |  |
| results | jsonb | YES | '{}'::jsonb |
| notes | text | YES | ''::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |
| valid_until | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_kyc_verifications_pkey`

---

## charvak_kyc_verified_users

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| name | text | YES |  |
| verification_id | text | YES |  |
| verification_type | text | YES |  |
| verified_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| valid_until | timestamp without time zone | YES |  |
| badge_id | text | YES |  |

**Indexes:**

- `charvak_kyc_verified_users_badge_id_key`
- `charvak_kyc_verified_users_pkey`

---

## charvak_lang_ai_assessments

| Column | Type | Nullable | Default |
|---|---|---|---|
| assessment_id | text | NO |  |
| language | text | YES |  |
| native_name | text | YES |  |
| skill | text | YES |  |
| difficulty | text | YES | 'Beginner'::text |
| questions | jsonb | YES | '[]'::jsonb |
| total_questions | integer | YES | 0 |
| passing_score | integer | YES | 70 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lang_ai_assessments_pkey`
- `idx_lang_ai_created`
- `idx_lang_ai_language`
- `idx_lang_ai_skill`

---

## charvak_lang_ai_submissions

| Column | Type | Nullable | Default |
|---|---|---|---|
| submission_id | text | NO |  |
| assessment_id | text | NO |  |
| email | text | YES |  |
| answers | jsonb | YES | '[]'::jsonb |
| score | integer | YES | 0 |
| passed | boolean | YES | false |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lang_ai_submissions_pkey`
- `idx_lang_ai_subs_assessment`
- `idx_lang_ai_subs_email`
- `idx_lang_ai_subs_submitted`

---

## charvak_legacy_shift_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| report_id | text | NO |  |
| email | text | NO |  |
| code_preview | text | YES |  |
| analysis_json | jsonb | YES |  |
| plan_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_legacy_shift_reports_pkey`

---

## charvak_lms_certificates

| Column | Type | Nullable | Default |
|---|---|---|---|
| certificate_id | text | NO |  |
| course_name | text | YES |  |
| student_email | text | NO |  |
| student_name | text | YES | 'Student'::text |
| issued_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| verification_url | text | YES |  |

**Indexes:**

- `charvak_lms_certificates_pkey`

---

## charvak_lms_discussions

| Column | Type | Nullable | Default |
|---|---|---|---|
| discussion_id | text | NO |  |
| course_id | text | NO |  |
| author | text | YES |  |
| title | text | YES |  |
| content | text | YES |  |
| replies | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_discussions_pkey`

---

## charvak_lms_enrollments

| Column | Type | Nullable | Default |
|---|---|---|---|
| enrollment_id | text | NO |  |
| email | text | NO |  |
| course_id | text | NO |  |
| course_name | text | YES |  |
| price_inr | integer | YES |  |
| credits_used | integer | NO | 0 |
| enrolled_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_lms_enrollments_email_course_id_key`
- `charvak_lms_enrollments_pkey`

---

## charvak_lms_lesson_progress

| Column | Type | Nullable | Default |
|---|---|---|---|
| progress_id | text | NO |  |
| enrollment_id | text | NO |  |
| lesson_id | text | NO |  |
| completed | boolean | YES | true |
| time_spent_minutes | integer | YES | 0 |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_lesson_progress_pkey`

---

## charvak_lms_lessons

| Column | Type | Nullable | Default |
|---|---|---|---|
| lesson_id | text | NO |  |
| course_id | text | NO |  |
| title | text | YES | 'Lesson'::text |
| video_url | text | YES | ''::text |
| duration_minutes | integer | YES | 10 |
| lesson_order | integer | YES | 1 |

**Indexes:**

- `charvak_lms_lessons_pkey`

---

## charvak_lms_payouts

| Column | Type | Nullable | Default |
|---|---|---|---|
| payout_id | text | NO |  |
| trainer_email | text | NO |  |
| amount | numeric | YES | 0 |
| status | text | YES | 'pending'::text |
| requested_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_payouts_pkey`

---

## charvak_lms_quiz_attempts

| Column | Type | Nullable | Default |
|---|---|---|---|
| attempt_id | text | NO |  |
| quiz_id | text | YES |  |
| course_id | text | YES |  |
| student_email | text | NO |  |
| score | integer | YES | 0 |
| passed | boolean | YES | false |
| attempted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_quiz_attempts_pkey`

---

## charvak_lms_quizzes

| Column | Type | Nullable | Default |
|---|---|---|---|
| quiz_id | text | NO |  |
| course_id | text | NO |  |
| title | text | YES | 'Course Quiz'::text |
| questions | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_quizzes_pkey`

---

## charvak_lms_ratings

| Column | Type | Nullable | Default |
|---|---|---|---|
| rating_id | text | NO |  |
| course_id | text | NO |  |
| student_email | text | NO |  |
| rating | integer | NO |  |
| review | text | YES | ''::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lms_ratings_pkey`

---

## charvak_lock_in_engagements

| Column | Type | Nullable | Default |
|---|---|---|---|
| engagement_id | text | NO |  |
| email | text | NO |  |
| tier | text | NO |  |
| audit_id | text | YES |  |
| provider | text | YES |  |
| monthly_spend | numeric | YES |  |
| services_json | jsonb | YES |  |
| plan_json | jsonb | YES |  |
| expires_at | timestamp without time zone | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_lock_in_engagements_pkey`
- `idx_lock_in_engagements_audit`
- `idx_lock_in_engagements_email`
- `idx_lock_in_engagements_tier`

---

## charvak_marketing_booking_kits

| Column | Type | Nullable | Default |
|---|---|---|---|
| kit_id | text | NO |  |
| email | text | NO |  |
| host_name | text | YES |  |
| business_name | text | YES |  |
| meeting_type | text | YES |  |
| duration_min | integer | YES |  |
| context | text | YES |  |
| kit_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| slug | text | YES |  |
| host_email | text | YES |  |
| booking_url | text | YES |  |

**Indexes:**

- `charvak_marketing_booking_kits_pkey`

---

## charvak_marketing_job_ads

| Column | Type | Nullable | Default |
|---|---|---|---|
| ad_id | text | NO |  |
| job_title | text | YES |  |
| company | text | YES |  |
| ad_text | text | YES |  |
| platforms | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_marketing_job_ads_pkey`
- `idx_marketing_ads_company`
- `idx_marketing_ads_title`

---

## charvak_marketing_lead_drips

| Column | Type | Nullable | Default |
|---|---|---|---|
| drip_id | text | NO |  |
| lead_name | text | YES |  |
| lead_email | text | YES |  |
| service | text | YES |  |
| sequence | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_marketing_lead_drips_pkey`
- `idx_marketing_drips_email`
- `idx_marketing_drips_service`

---

## charvak_marketing_social_posts

| Column | Type | Nullable | Default |
|---|---|---|---|
| post_id | text | NO |  |
| topic | text | YES |  |
| platform | text | YES |  |
| audience | text | YES |  |
| post_text | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_marketing_social_posts_pkey`
- `idx_marketing_posts_platform`

---

## charvak_master_profiles

| Column | Type | Nullable | Default |
|---|---|---|---|
| profile_id | text | NO |  |
| email | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_master_profiles_email_key`
- `charvak_master_profiles_pkey`
- `idx_master_profiles_email`

---

## charvak_messages

| Column | Type | Nullable | Default |
|---|---|---|---|
| message_id | text | NO |  |
| sender_id | text | NO |  |
| sender_type | text | YES |  |
| recipient_id | text | NO |  |
| recipient_type | text | YES |  |
| subject | text | YES | 'New Message'::text |
| body | text | YES | ''::text |
| job_id | text | YES |  |
| application_id | text | YES |  |
| status | text | YES | 'sent'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| read_at | timestamp without time zone | YES |  |
| conversation_key | text | NO |  |

**Indexes:**

- `charvak_messages_pkey`
- `idx_messages_convo`
- `idx_messages_created`
- `idx_messages_recipient`
- `idx_messages_sender`
- `idx_messages_status`

---

## charvak_micro_applications

| Column | Type | Nullable | Default |
|---|---|---|---|
| application_id | text | NO |  |
| project_id | text | NO |  |
| candidate_name | text | YES |  |
| candidate_email | text | YES |  |
| skills | jsonb | YES | '[]'::jsonb |
| portfolio_url | text | YES | ''::text |
| why_interested | text | YES | ''::text |
| status | text | YES | 'applied'::text |
| ai_score | integer | YES | 0 |
| applied_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| assigned_at | timestamp without time zone | YES |  |
| submitted_at | timestamp without time zone | YES |  |
| approved_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_micro_applications_pkey`

---

## charvak_micro_clients

| Column | Type | Nullable | Default |
|---|---|---|---|
| client_id | text | NO |  |
| company_name | text | NO |  |
| contact_email | text | NO |  |
| contact_name | text | YES |  |
| industry | text | YES | ''::text |
| company_size | text | YES | ''::text |
| total_projects | integer | YES | 0 |
| active_projects | integer | YES | 0 |
| total_spend | numeric | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_micro_clients_pkey`

---

## charvak_micro_projects

| Column | Type | Nullable | Default |
|---|---|---|---|
| project_id | text | NO |  |
| title | text | NO |  |
| category | text | YES | 'Web Development'::text |
| difficulty | text | YES | 'Intermediate'::text |
| duration_weeks | integer | YES | 2 |
| budget_inr | numeric | NO |  |
| budget_usd | numeric | YES |  |
| skills_required | jsonb | YES | '[]'::jsonb |
| description | text | YES | ''::text |
| client_id | text | YES |  |
| company_name | text | YES |  |
| contact_email | text | YES |  |
| escrow_required | boolean | YES | true |
| escrow_id | text | YES |  |
| assigned_intern | jsonb | YES |  |
| status | text | YES | 'open'::text |
| applications_count | integer | YES | 0 |
| milestones | jsonb | YES | '[]'::jsonb |
| submission | jsonb | YES |  |
| feedback | text | YES |  |
| rating | integer | YES |  |
| deadline | timestamp without time zone | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_micro_projects_pkey`

---

## charvak_micro_squad_leads

| Column | Type | Nullable | Default |
|---|---|---|---|
| lead_id | text | NO |  |
| name | text | NO |  |
| email | text | NO |  |
| phone | text | YES |  |
| company | text | YES |  |
| requirement | text | YES |  |
| project_type | text | YES |  |
| duration_days | integer | YES |  |
| budget | integer | YES |  |
| squad_id | text | YES |  |
| source | text | YES | 'micro-squads'::text |
| status | text | YES | 'new'::text |
| contacted_at | timestamp without time zone | YES |  |
| notes | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_micro_squad_leads_pkey`

---

## charvak_mock_answers

| Column | Type | Nullable | Default |
|---|---|---|---|
| answer_id | text | NO |  |
| session_id | text | NO |  |
| section_name | text | NO |  |
| question_id | integer | NO |  |
| selected | integer | NO |  |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_mock_answers_pkey`
- `charvak_mock_answers_session_id_section_name_question_id_key`

---

## charvak_mock_sessions

| Column | Type | Nullable | Default |
|---|---|---|---|
| session_id | text | NO |  |
| email | text | NO |  |
| company_id | text | NO |  |
| company_name | text | NO |  |
| pattern | text | NO |  |
| sections_json | jsonb | NO |  |
| total_questions | integer | NO |  |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |
| status | text | NO | 'in_progress'::text |
| score | numeric | YES |  |
| correct_count | integer | YES |  |
| passed | boolean | YES |  |

**Indexes:**

- `charvak_mock_sessions_pkey`

---

## charvak_monitor_alert_history

| Column | Type | Nullable | Default |
|---|---|---|---|
| alert_id | text | NO |  |
| url | text | NO |  |
| name | text | YES |  |
| issues | jsonb | YES | '[]'::jsonb |
| checked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_monitor_alert_history_pkey`
- `idx_monitor_alerts_checked`
- `idx_monitor_alerts_url`

---

## charvak_monitor_sites

| Column | Type | Nullable | Default |
|---|---|---|---|
| url | text | NO |  |
| name | text | YES |  |
| interval_seconds | integer | YES | 300 |
| status | text | YES | 'unknown'::text |
| last_check | timestamp without time zone | YES |  |
| issues | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_monitor_sites_pkey`
- `idx_monitor_sites_status`

---

## charvak_na_compliance_reports

| Column | Type | Nullable | Default |
|---|---|---|---|
| report_id | text | NO |  |
| report_type | text | NO |  |
| job_id | text | YES |  |
| candidate_id | text | YES |  |
| eeoc_compliant | boolean | YES |  |
| nyc_law_144_applicable | boolean | YES |  |
| issues | jsonb | YES | '[]'::jsonb |
| warnings | jsonb | YES | '[]'::jsonb |
| restrictions | jsonb | YES | '[]'::jsonb |
| checked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_compliance_reports_pkey`
- `idx_na_comp_candidate`
- `idx_na_comp_job`
- `idx_na_comp_type`

---

## charvak_na_cvms_requisitions

| Column | Type | Nullable | Default |
|---|---|---|---|
| req_id | text | NO |  |
| client_id | text | NO |  |
| title | text | YES |  |
| description | text | YES | ''::text |
| skills_required | jsonb | YES | '[]'::jsonb |
| rate_range | jsonb | YES | '{}'::jsonb |
| location | text | YES | 'Remote'::text |
| duration | text | YES | '6 months'::text |
| visa_restrictions | jsonb | YES | '[]'::jsonb |
| submission_limit | integer | YES | 3 |
| status | text | YES | 'Open - Accepting Submissions'::text |
| submissions_count | integer | YES | 0 |
| interviews_scheduled | integer | YES | 0 |
| offer_extended | boolean | YES | false |
| timeline | jsonb | YES | '[]'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_cvms_requisitions_pkey`
- `idx_na_cvms_req_client`
- `idx_na_cvms_req_status`

---

## charvak_na_cvms_sow_contracts

| Column | Type | Nullable | Default |
|---|---|---|---|
| sow_id | text | NO |  |
| client_id | text | NO |  |
| vendor_id | text | NO |  |
| title | text | YES |  |
| description | text | YES |  |
| deliverables | jsonb | YES | '[]'::jsonb |
| total_value | numeric | YES | 0 |
| start_date | text | YES |  |
| end_date | text | YES |  |
| milestones | jsonb | YES | '[]'::jsonb |
| payment_schedule | jsonb | YES | '[]'::jsonb |
| status | text | YES | 'Active'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_cvms_sow_contracts_pkey`
- `idx_na_cvms_sow_client`
- `idx_na_cvms_sow_status`
- `idx_na_cvms_sow_vendor`

---

## charvak_na_cvms_timecards

| Column | Type | Nullable | Default |
|---|---|---|---|
| timecard_id | text | NO |  |
| req_id | text | NO |  |
| candidate_id | text | YES |  |
| hours | numeric | YES | 0 |
| rate | numeric | YES | 0 |
| gross_amount | numeric | YES | 0 |
| charvak_fee | numeric | YES | 0 |
| net_amount | numeric | YES | 0 |
| period_end | text | YES |  |
| status | text | YES | 'Submitted for Approval'::text |
| payment_triggered | boolean | YES | false |
| payment_reference | text | YES |  |
| approval_history | jsonb | YES | '[]'::jsonb |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_cvms_timecards_pkey`
- `idx_na_cvms_tc_candidate`
- `idx_na_cvms_tc_req`
- `idx_na_cvms_tc_status`

---

## charvak_na_match_history

| Column | Type | Nullable | Default |
|---|---|---|---|
| match_id | text | NO |  |
| candidate_id | text | YES |  |
| matches_count | integer | YES | 0 |
| top_score | integer | YES | 0 |
| matched_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_match_history_pkey`
- `idx_na_match_candidate`
- `idx_na_match_time`

---

## charvak_na_redaction_log

| Column | Type | Nullable | Default |
|---|---|---|---|
| log_id | text | NO |  |
| candidate_id | text | YES |  |
| redactions | jsonb | YES | '{}'::jsonb |
| original_length | integer | YES | 0 |
| redacted_length | integer | YES | 0 |
| redacted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_redaction_log_pkey`
- `idx_na_redact_candidate`
- `idx_na_redact_time`

---

## charvak_na_revenue_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| firm_id | text | NO |  |
| subscription_id | text | YES |  |
| tier | text | YES |  |
| bench_limit | integer | YES | 0 |
| features | jsonb | YES | '[]'::jsonb |
| monthly_fee | numeric | YES | 0 |
| status | text | YES | 'active'::text |
| start_date | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| next_billing | timestamp without time zone | YES |  |
| payment_method | text | YES |  |
| auto_renew | boolean | YES | true |

**Indexes:**

- `charvak_na_revenue_subscriptions_pkey`
- `idx_na_rev_subs_status`
- `idx_na_rev_subs_tier`

---

## charvak_na_revenue_transactions

| Column | Type | Nullable | Default |
|---|---|---|---|
| transaction_id | text | NO |  |
| firm_id | text | NO |  |
| stream | text | NO |  |
| amount | numeric | YES | 0 |
| details | jsonb | YES | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_revenue_transactions_pkey`
- `idx_na_rev_txn_firm`
- `idx_na_rev_txn_stream`
- `idx_na_rev_txn_time`

---

## charvak_na_sub_vendor_submissions

| Column | Type | Nullable | Default |
|---|---|---|---|
| submission_key | text | NO |  |
| vendor_id | text | NO |  |
| candidate_id | text | YES |  |
| job_id | text | YES |  |
| status | text | YES | 'submitted'::text |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_sub_vendor_submissions_pkey`
- `idx_na_vendor_subs_candidate`
- `idx_na_vendor_subs_status`
- `idx_na_vendor_subs_vendor`

---

## charvak_na_sub_vendors

| Column | Type | Nullable | Default |
|---|---|---|---|
| vendor_id | text | NO |  |
| name | text | YES |  |
| tier | text | YES | 'Tier-2'::text |
| email | text | YES |  |
| specialization | jsonb | YES | '[]'::jsonb |
| active_candidates | integer | YES | 0 |
| successful_placements | integer | YES | 0 |
| status | text | YES | 'active'::text |
| registered_date | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_sub_vendors_pkey`
- `idx_na_vendors_email`
- `idx_na_vendors_status`

---

## charvak_na_verified_candidates

| Column | Type | Nullable | Default |
|---|---|---|---|
| candidate_id | text | NO |  |
| visa_type | text | YES |  |
| visa_validity_years | text | YES |  |
| auth_status | text | YES |  |
| can_submit | boolean | YES | false |
| compatibility | jsonb | YES | '{}'::jsonb |
| required_documents | jsonb | YES | '[]'::jsonb |
| compliance_requirements | jsonb | YES | '[]'::jsonb |
| restrictions | jsonb | YES | '[]'::jsonb |
| client_type | text | YES | 'corporate'::text |
| verified_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_verified_candidates_pkey`
- `idx_na_wa_candidates_status`
- `idx_na_wa_candidates_submit`
- `idx_na_wa_candidates_visa`

---

## charvak_na_vms_jobs

| Column | Type | Nullable | Default |
|---|---|---|---|
| job_id | text | NO |  |
| source | text | YES |  |
| title | text | YES |  |
| client | text | YES |  |
| vms_provider | text | YES |  |
| location | text | YES |  |
| rate_range | jsonb | YES | '{}'::jsonb |
| skills_required | jsonb | YES | '[]'::jsonb |
| visa_restrictions | jsonb | YES | '[]'::jsonb |
| duration | text | YES |  |
| status | text | YES | 'Active - Accepting Submissions'::text |
| posted_date | text | YES |  |
| submission_deadline | text | YES |  |
| submission_limit | integer | YES | 3 |
| interview_process | text | YES |  |
| compliance_notes | text | YES |  |
| ghost_score | numeric | YES | 0 |
| is_ghost | boolean | YES | false |
| ingested_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_vms_jobs_pkey`
- `idx_na_vms_jobs_ghost`
- `idx_na_vms_jobs_source`
- `idx_na_vms_jobs_status`

---

## charvak_na_vms_submissions

| Column | Type | Nullable | Default |
|---|---|---|---|
| submission_id | text | NO |  |
| job_id | text | NO |  |
| candidate_id | text | YES |  |
| vendor_id | text | YES |  |
| status | text | YES | 'Submitted'::text |
| work_auth | jsonb | YES | '{}'::jsonb |
| timeline | jsonb | YES | '[]'::jsonb |
| submitted_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_na_vms_submissions_pkey`
- `idx_na_vms_subs_candidate`
- `idx_na_vms_subs_job`
- `idx_na_vms_subs_status`

---

## charvak_network_tracker

| Column | Type | Nullable | Default |
|---|---|---|---|
| track_id | text | NO |  |
| email | text | NO |  |
| connection_name | text | YES |  |
| company | text | YES |  |
| status | text | YES | 'pending'::text |
| tracked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_network_tracker_pkey`
- `idx_ntracker_company`
- `idx_ntracker_email`

---

## charvak_notifications

| Column | Type | Nullable | Default |
|---|---|---|---|
| notification_id | text | NO |  |
| to_email | text | NO |  |
| subject | text | YES |  |
| html_content | text | YES |  |
| status | text | YES | 'sent'::text |
| error_message | text | YES |  |
| sent_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_notifications_pkey`
- `idx_notifications_sent`
- `idx_notifications_status`
- `idx_notifications_to`

---

## charvak_outreach_auto_tracked

| Column | Type | Nullable | Default |
|---|---|---|---|
| track_id | text | NO |  |
| email | text | NO |  |
| company | text | YES |  |
| role | text | YES |  |
| status | text | YES | 'applied'::text |
| tracked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_outreach_auto_tracked_pkey`
- `idx_outreach_tracked_company`
- `idx_outreach_tracked_email`

---

## charvak_outreach_cold_emails

| Column | Type | Nullable | Default |
|---|---|---|---|
| email_id | text | NO |  |
| company | text | YES |  |
| hiring_manager | text | YES |  |
| domain | text | YES |  |
| likely_emails | jsonb | YES | '[]'::jsonb |
| confidence | text | YES |  |
| cold_email_template | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_outreach_cold_emails_pkey`
- `idx_outreach_ce_company`
- `idx_outreach_ce_domain`

---

## charvak_outreach_email_syncs

| Column | Type | Nullable | Default |
|---|---|---|---|
| sync_id | text | NO |  |
| email | text | NO |  |
| sync_type | text | YES | 'all'::text |
| status | text | YES | 'connected'::text |
| connected_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_outreach_email_syncs_email_key`
- `charvak_outreach_email_syncs_pkey`
- `idx_outreach_syncs_email`

---

## charvak_outreach_premium_users

| Column | Type | Nullable | Default |
|---|---|---|---|
| subscription_id | text | NO |  |
| email | text | NO |  |
| plan | text | YES | 'basic'::text |
| price | integer | YES | 0 |
| features | jsonb | YES | '[]'::jsonb |
| subscribed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_outreach_premium_users_email_key`
- `charvak_outreach_premium_users_pkey`
- `idx_outreach_premium_email`
- `idx_outreach_premium_plan`

---

## charvak_payment_log

| Column | Type | Nullable | Default |
|---|---|---|---|
| order_id | text | NO |  |
| status | text | YES |  |
| amount | numeric | YES | 0 |
| raw_data | jsonb | NO | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_payment_log_pkey`
- `idx_payment_log_created`
- `idx_payment_log_status`

---

## charvak_product_results

| Column | Type | Nullable | Default |
|---|---|---|---|
| result_id | text | NO |  |
| product_type | text | NO |  |
| email | text | YES |  |
| input_data | jsonb | NO | '{}'::jsonb |
| result_data | jsonb | NO | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_product_results_pkey`
- `idx_product_results_created`
- `idx_product_results_email`
- `idx_product_results_type`

---

## charvak_referral_bounties

| Column | Type | Nullable | Default |
|---|---|---|---|
| bounty_id | text | NO |  |
| referral_code | text | NO |  |
| referrer_email | text | NO |  |
| new_user_email | text | YES |  |
| amount_inr | integer | YES | 500 |
| status | text | YES | 'signed_up'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| paid_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_referral_bounties_pkey`

---

## charvak_referral_clicks

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | integer | NO | nextval('charvak_referral_clicks_id_s... |
| referral_code | text | NO |  |
| source | text | YES | 'direct'::text |
| clicked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_referral_clicks_pkey`

---

## charvak_referrals

| Column | Type | Nullable | Default |
|---|---|---|---|
| referral_code | text | NO |  |
| referral_link | text | NO |  |
| referrer_name | text | YES |  |
| referrer_email | text | NO |  |
| user_type | text | YES | 'candidate'::text |
| clicks | integer | YES | 0 |
| signups | integer | YES | 0 |
| conversions | integer | YES | 0 |
| total_earned | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_referrals_pkey`

---

## charvak_reverse_staffing_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| tier | text | NO | 'subscription'::text |
| started_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |
| matches_used | integer | NO | 0 |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_reverse_staffing_subscriptions_pkey`

---

## charvak_role_manager_custom_roles

| Column | Type | Nullable | Default |
|---|---|---|---|
| role_id | text | NO |  |
| name | text | YES |  |
| category | text | YES |  |
| skills | jsonb | YES | '[]'::jsonb |
| description | text | YES | ''::text |
| skills_count | integer | YES | 0 |
| status | text | YES | 'active'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_role_manager_custom_roles_pkey`
- `idx_rm_roles_category`
- `idx_rm_roles_status`

---

## charvak_silent_killer_scans

| Column | Type | Nullable | Default |
|---|---|---|---|
| scan_id | text | NO |  |
| watch_id | text | NO |  |
| email | text | NO |  |
| url | text | NO |  |
| status_code | integer | YES |  |
| response_ms | integer | YES |  |
| ok | boolean | NO |  |
| error | text | YES |  |
| checked_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_silent_killer_scans_pkey`
- `idx_sk_scans_email_time`
- `idx_sk_scans_watch_time`

---

## charvak_silent_killer_watches

| Column | Type | Nullable | Default |
|---|---|---|---|
| watch_id | text | NO |  |
| email | text | NO |  |
| url | text | NO |  |
| name | text | YES |  |
| interval_minutes | integer | NO | 5 |
| active | boolean | NO | true |
| last_scan_at | timestamp without time zone | YES |  |
| last_status | text | YES |  |
| last_status_code | integer | YES |  |
| last_error | text | YES |  |
| alert_count | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_silent_killer_watches_pkey`
- `idx_sk_watches_active_lastscan`
- `idx_sk_watches_email_active`

---

## charvak_skill_gaps

| Column | Type | Nullable | Default |
|---|---|---|---|
| user_id | text | NO |  |
| skill_gaps | jsonb | YES |  |
| recommended_courses | jsonb | YES |  |
| synced_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_skill_gaps_pkey`

---

## charvak_skill_twin_results

| Column | Type | Nullable | Default |
|---|---|---|---|
| check_id | text | NO |  |
| email | text | NO |  |
| twin_id | text | YES |  |
| skills_json | jsonb | YES |  |
| experience | integer | YES |  |
| self_rating | numeric | YES |  |
| verified_score | integer | YES |  |
| gap | numeric | YES |  |
| skill_level | text | YES |  |
| badge_eligible | boolean | YES | false |
| badge_issued | boolean | YES | false |
| badge_id | text | YES |  |
| result_json | jsonb | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| badge_issued_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_skill_twin_results_pkey`
- `idx_skill_twin_badge_eligible`
- `idx_skill_twin_badge_id`
- `idx_skill_twin_email`

---

## charvak_student_suite_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| plan | text | NO | 'free'::text |
| requests_used | integer | YES | 0 |
| subscribed_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_student_suite_subscriptions_pkey`
- `idx_student_subs_plan`

---

## charvak_student_suite_usage

| Column | Type | Nullable | Default |
|---|---|---|---|
| usage_id | text | NO |  |
| email | text | NO |  |
| feature | text | NO |  |
| count | integer | YES | 1 |
| last_used_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_student_suite_usage_email_feature_key`
- `charvak_student_suite_usage_pkey`
- `idx_student_usage_email`
- `idx_student_usage_feature`

---

## charvak_synced_applications

| Column | Type | Nullable | Default |
|---|---|---|---|
| application_id | text | NO |  |
| user_id | text | YES |  |
| job_title | text | YES |  |
| company | text | YES |  |
| job_url | text | YES |  |
| status | text | YES |  |
| applied_date | text | YES |  |
| source | text | YES | 'charvakit'::text |
| notes | text | YES |  |
| last_updated | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_synced_applications_pkey`

---

## charvak_synced_users

| Column | Type | Nullable | Default |
|---|---|---|---|
| user_id | text | NO |  |
| doketsrb_id | text | YES |  |
| name | text | YES |  |
| email | text | YES |  |
| phone | text | YES |  |
| resume_data | jsonb | YES |  |
| skills | jsonb | YES |  |
| experience | jsonb | YES |  |
| education | jsonb | YES |  |
| synced_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_synced_users_pkey`

---

## charvak_team_members

| Column | Type | Nullable | Default |
|---|---|---|---|
| member_id | text | NO |  |
| team_id | text | NO |  |
| name | text | YES |  |
| email | text | NO |  |
| role | text | NO | 'recruiter'::text |
| joined_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_team_members_pkey`
- `charvak_team_members_team_id_email_key`
- `idx_team_members_email`
- `idx_team_members_role`
- `idx_team_members_team`

---

## charvak_team_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| tier | text | NO | 'pro'::text |
| started_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |
| max_members | integer | NO | 20 |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_team_subscriptions_pkey`
- `idx_team_subs_expires`

---

## charvak_teams

| Column | Type | Nullable | Default |
|---|---|---|---|
| team_id | text | NO |  |
| company_name | text | YES |  |
| admin_email | text | YES |  |
| admin_name | text | YES |  |
| member_count | integer | YES | 1 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_teams_pkey`
- `idx_teams_admin_email`

---

## charvak_tool_results

| Column | Type | Nullable | Default |
|---|---|---|---|
| result_id | text | NO |  |
| email | text | NO |  |
| tool_name | text | NO |  |
| inputs_json | jsonb | YES |  |
| result_json | jsonb | YES |  |
| credits_used | integer | NO | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_tool_results_pkey`

---

## charvak_training_courses

| Column | Type | Nullable | Default |
|---|---|---|---|
| course_id | text | NO |  |
| course_name | text | NO |  |
| trainer_name | text | YES |  |
| trainer_email | text | NO |  |
| category | text | YES | 'Programming'::text |
| duration_weeks | integer | YES | 4 |
| price_inr | numeric | NO | 0 |
| platform_fee | numeric | YES | 0 |
| trainer_payout | numeric | YES | 0 |
| description | text | YES | ''::text |
| skills | jsonb | YES | '[]'::jsonb |
| schedule | text | YES | 'Flexible'::text |
| status | text | YES | 'published'::text |
| enrolled_count | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_training_courses_pkey`

---

## charvak_training_enrollments

| Column | Type | Nullable | Default |
|---|---|---|---|
| enrollment_id | text | NO |  |
| course_id | text | NO |  |
| student_name | text | YES |  |
| student_email | text | NO |  |
| payment_status | text | YES | 'pending'::text |
| payment_id | text | YES |  |
| progress_percent | integer | YES | 0 |
| enrolled_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| completed_at | timestamp without time zone | YES |  |

**Indexes:**

- `charvak_training_enrollments_pkey`

---

## charvak_training_plans

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| data | jsonb | NO | '{}'::jsonb |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_training_plans_pkey`
- `idx_training_created`

---

## charvak_universities

| Column | Type | Nullable | Default |
|---|---|---|---|
| university_id | text | NO |  |
| name | text | YES |  |
| admin_email | text | YES |  |
| location | text | YES | ''::text |
| type | text | YES | 'University'::text |
| student_count | integer | YES | 0 |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_universities_pkey`
- `idx_universities_admin`
- `idx_universities_name`

---

## charvak_university_outcomes

| Column | Type | Nullable | Default |
|---|---|---|---|
| outcome_id | text | NO |  |
| student_id | text | NO |  |
| outcome_type | text | YES | 'employed'::text |
| company_name | text | YES | ''::text |
| salary | numeric | YES | 0 |
| job_title | text | YES | ''::text |
| location | text | YES | ''::text |
| recorded_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_university_outcomes_pkey`
- `idx_unioutcomes_student`
- `idx_unioutcomes_type`

---

## charvak_university_students

| Column | Type | Nullable | Default |
|---|---|---|---|
| student_id | text | NO |  |
| university_id | text | NO |  |
| name | text | YES |  |
| email | text | YES |  |
| graduation_year | integer | YES | 2026 |
| status | text | YES | 'enrolled'::text |
| placement_status | text | YES | 'not_placed'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_university_students_pkey`
- `idx_unistudents_email`
- `idx_unistudents_placement`
- `idx_unistudents_university`

---

## charvak_university_subscriptions

| Column | Type | Nullable | Default |
|---|---|---|---|
| university_id | text | NO |  |
| admin_email | text | NO |  |
| tier | text | NO |  |
| price_inr | integer | YES |  |
| credits_used | integer | NO | 0 |
| started_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| expires_at | timestamp without time zone | NO |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_university_subscriptions_pkey`
- `idx_univ_subs_admin`
- `idx_univ_subs_expires`

---

## charvak_user_ability

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| skill | text | NO |  |
| ability_score | numeric | NO | 1000.0 |
| attempts | integer | NO | 0 |
| correct_total | integer | NO | 0 |
| question_total | integer | NO | 0 |
| last_updated | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_user_ability_pkey`
- `idx_user_ability_email`
- `idx_user_ability_skill`

---

## charvak_user_credits

| Column | Type | Nullable | Default |
|---|---|---|---|
| email | text | NO |  |
| plan | text | NO | 'free'::text |
| credits_remaining | integer | NO | 0 |
| total_credits_used | integer | NO | 0 |
| total_ai_calls | integer | NO | 0 |
| daily_usage | jsonb | NO | '{}'::jsonb |
| last_daily_bonus | date | YES |  |
| expires_at | timestamp without time zone | NO |  |
| created_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | NO | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_user_credits_pkey`

---

## charvak_voice_to_web_domains

| Column | Type | Nullable | Default |
|---|---|---|---|
| website_id | text | NO |  |
| domain | text | NO |  |
| status | text | YES | 'pending_setup'::text |
| dns_configured | boolean | YES | false |
| ssl_active | boolean | YES | false |
| setup_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_voice_to_web_domains_pkey`

---

## charvak_voice_to_web_seo

| Column | Type | Nullable | Default |
|---|---|---|---|
| website_id | text | NO |  |
| meta_title | text | YES |  |
| meta_description | text | YES |  |
| keywords | jsonb | YES | '[]'::jsonb |
| og_tags | boolean | YES | true |
| twitter_cards | boolean | YES | true |
| sitemap | boolean | YES | true |
| robots_txt | boolean | YES | true |
| structured_data | jsonb | YES | '{}'::jsonb |
| enabled_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_voice_to_web_seo_pkey`

---

## charvak_voice_to_web_sites

| Column | Type | Nullable | Default |
|---|---|---|---|
| website_id | text | NO |  |
| email | text | NO |  |
| business_name | text | NO |  |
| plan | text | YES | 'free'::text |
| transcript | text | YES | ''::text |
| custom_domain | text | YES |  |
| branding | text | YES | 'charvak'::text |
| seo_enabled | boolean | YES | false |
| updates_enabled | boolean | YES | false |
| priority_support | boolean | YES | false |
| status | text | YES | 'live'::text |
| url | text | YES |  |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| html_content | text | YES |  |
| slug | text | YES |  |

**Indexes:**

- `charvak_voice_to_web_sites_pkey`
- `idx_v2w_sites_email`
- `idx_v2w_sites_plan`
- `idx_v2w_sites_slug`

---

## charvak_voice_to_web_tickets

| Column | Type | Nullable | Default |
|---|---|---|---|
| ticket_id | text | NO |  |
| email | text | NO |  |
| issue | text | NO |  |
| website_id | text | YES |  |
| priority | text | YES | 'normal'::text |
| status | text | YES | 'open'::text |
| response_time | text | YES | '24 hours'::text |
| created_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |

**Indexes:**

- `charvak_voice_to_web_tickets_pkey`
- `idx_v2w_tickets_email`
- `idx_v2w_tickets_site`

---

## charvak_voice_to_web_updates

| Column | Type | Nullable | Default |
|---|---|---|---|
| update_id | text | NO |  |
| website_id | text | NO |  |
| type | text | YES |  |
| details | text | YES |  |
| email | text | YES | ''::text |
| status | text | YES | 'queued'::text |
| priority | text | YES | 'normal'::text |
| requested_at | timestamp without time zone | YES | CURRENT_TIMESTAMP |
| estimated_completion | text | YES | '24 hours'::text |

**Indexes:**

- `charvak_voice_to_web_updates_pkey`
- `idx_v2w_updates_site`

---
