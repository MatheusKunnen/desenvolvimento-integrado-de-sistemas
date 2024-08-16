# desenvolvimento-integrado-de-sistemas

# API Servidor

## POST /image

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

## GET /image/:job_id

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

## GET /image/:job_id/image

Response: `PNG image`
