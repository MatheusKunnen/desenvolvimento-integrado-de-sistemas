# desenvolvimento-integrado-de-sistemas

# API Servidor

## POST /job

Request:

```
{
  user: string,
  use_gain: boolean,
  model: 1 | 2,
  signal: number[]
}
```

Response:

```
{
  job_id: string
}
```

## GET /job/:job_id

**OBS:** com o parametro `?minimal=true` retorna unicamente o status.

Response:

```
{
  status: 'pending' | 'done'
  job_id: string
  user: string
  use_gain: boolean
  model: 1 | 2
  algorithm: 'cgnr'
  image_size: string
  created_at: Date
  started_at: Date | null
  finished_at: Date | null
  iterations: number | null
}
```

## GET /job/image/:job_id

Response: `PNG image`
