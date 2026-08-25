export type FtpFields = {
  host: string
  username: string
  password: string
  in_path: string
  out_path: string
  print_path: string
  archive_path: string
  error_path: string
}

export const FTP_PATH_FIELDS = [
  {
    key: 'in_path',
    label: 'Папка входящих',
    hint: 'откуда забираем заявки',
  },
  {
    key: 'out_path',
    label: 'Папка исходящих',
    hint: 'куда отправляем подтверждения',
  },
  {
    key: 'print_path',
    label: 'Папка печатных форм',
    hint: 'откуда берём PDF',
  },
  {
    key: 'archive_path',
    label: 'Папка архива',
    hint: 'успешно обработанные файлы',
  },
  {
    key: 'error_path',
    label: 'Папка ошибок',
    hint: 'файлы, которые не удалось принять',
  },
] as const

const EMPTY_FTP: FtpFields = {
  host: '',
  username: '',
  password: '',
  in_path: '/out',
  out_path: '/in',
  print_path: '/print',
  archive_path: '/archive',
  error_path: '/error',
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

export function ftpFromConfig(config: Record<string, unknown> | null | undefined): FtpFields {
  const ftp = asRecord(config?.ftp)
  return {
    host: String(ftp.host ?? ''),
    username: String(ftp.username ?? ''),
    password: String(ftp.password ?? ''),
    in_path: String(ftp.in_path ?? ''),
    out_path: String(ftp.out_path ?? ''),
    print_path: String(ftp.print_path ?? ''),
    archive_path: String(ftp.archive_path ?? ''),
    error_path: String(ftp.error_path ?? ''),
  }
}

export function restConfigWithoutFtp(
  config: Record<string, unknown> | null | undefined,
): Record<string, unknown> {
  if (!config) return {}
  const { ftp: _ftp, ...rest } = config
  return rest
}

export function buildConfig(
  ftp: FtpFields,
  previous: Record<string, unknown> = {},
): Record<string, unknown> {
  const next = { ...previous }
  next.ftp = {
    host: ftp.host.trim(),
    username: ftp.username.trim(),
    password: ftp.password,
    in_path: ftp.in_path.trim() || EMPTY_FTP.in_path,
    out_path: ftp.out_path.trim() || EMPTY_FTP.out_path,
    print_path: ftp.print_path.trim() || EMPTY_FTP.print_path,
    archive_path: ftp.archive_path.trim() || EMPTY_FTP.archive_path,
    error_path: ftp.error_path.trim() || EMPTY_FTP.error_path,
  }
  return next
}

export function emptyFtpForm(): FtpFields {
  return { ...EMPTY_FTP }
}
