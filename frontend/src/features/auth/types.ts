export interface LoginCredentials {
  email: string
  password: string
}

/** The plan of the active subscription, as returned by GET /auth/me/. */
export interface CurrentPlan {
  code: string
  name: string
  billing_cycle: 'monthly' | 'yearly'
  current_period_end: string | null
  max_monitors: number
  min_check_interval_sec: number
}

/** The logged-in client (GET /auth/me/); `plan` is null without an active subscription. */
export interface CurrentUser {
  id: number
  email: string
  first_name: string
  last_name: string
  timezone: string
  date_joined: string
  plan: CurrentPlan | null
}
