const API_BASE_URL = 'http://localhost:8000';

const FIELD_LABELS = {
  titulo: 'Título',
  descricao: 'Descrição',
  categoria: 'Categoria',
  prioridade: 'Prioridade',
  status: 'Status',
};

function formatFieldError(item) {
  const rawField = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null;
  const label = (rawField && FIELD_LABELS[rawField]) || rawField || 'Campo';

  if (item?.type === 'string_too_short' || item?.type === 'missing') {
    return `O campo "${label}" é obrigatório e não pode ficar vazio.`;
  }
  if (item?.type === 'enum') {
    return `Valor inválido selecionado para "${label}".`;
  }
  if (item?.type === 'string_type') {
    return `O campo "${label}" deve ser um texto válido.`;
  }
  return item?.msg ? `${label}: ${item.msg}` : 'Dados inválidos.';
}

// extractErrorMessage(data): handles string detail or Pydantic validation error array
export function extractErrorMessage(data) {
  const payload = data && data.detail !== undefined ? data.detail : data;

  if (typeof payload === 'string') {
    return payload;
  }

  if (Array.isArray(payload)) {
    if (payload.length === 0) {
      return 'Ocorreu um erro inesperado na validação dos dados.';
    }
    if (typeof payload[0] === 'string') {
      return payload.join(' ');
    }

    const requiredFields = payload
      .filter((item) => item?.type === 'string_too_short' || item?.type === 'missing')
      .map((item) => {
        const rawField = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null;
        return (rawField && FIELD_LABELS[rawField]) || rawField;
      })
      .filter(Boolean);

    if (requiredFields.length > 1 && requiredFields.length === payload.length) {
      return `Por favor, preencha os campos obrigatórios: ${requiredFields.join(', ')}.`;
    }

    return payload.map(formatFieldError).join(' ');
  }

  return 'Não foi possível processar a solicitação. Tente novamente.';
}

async function request(method, path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, { cache: 'no-store', ...options });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(extractErrorMessage(data));
    }
    return data;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Não foi possível conectar ao servidor. Verifique se a API está rodando.');
    }
    throw error;
  }
}

export async function listarSolicitacoes(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });
  const queryString = params.toString();
  const path = queryString ? `?${queryString}` : '';
  return request('GET', `/solicitacoes${path}`);
}

export async function obterSolicitacao(id) {
  return request('GET', `/solicitacoes/${id}`);
}

export async function criarSolicitacao(payload) {
  return request('POST', '/solicitacoes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function atualizarStatus(id, status) {
  return request('PATCH', `/solicitacoes/${id}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status }),
  });
}
