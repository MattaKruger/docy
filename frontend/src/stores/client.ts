import createClient from 'openapi-fetch'
import type { paths } from '../api.ts'

export const client = createClient<paths>({ baseUrl: 'http://localhost:8000' })
