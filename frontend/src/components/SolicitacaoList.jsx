import React from 'react';

// Defines the allowed progression of statuses.
// A value of null means there is no next step (e.g. 'Concluída').
const STATUS_FLOW = {
  'Aberta': 'Em andamento',
  'Em andamento': 'Concluída',
  'Concluída': null,
};

const NEXT_ACTION_LABEL = {
  'Aberta': 'Iniciar',
  'Em andamento': 'Concluir',
};

const PRIORITY_CLASSES = {
  baixa: 'badge-baixa',
  'média': 'badge-media',
  alta: 'badge-alta',
};

const STATUS_CLASSES = {
  Aberta: 'badge-aberta',
  'Em andamento': 'badge-andamento',
  Concluída: 'badge-concluida',
};

export default function SolicitacaoList({ solicitacoes, loading, onSelect, onAdvanceStatus }) {
  if (loading) {
    return (
      <div className="card">
        <h2>Solicitações</h2>
        Carregando...
      </div>
    );
  }

  if (!solicitacoes || solicitacoes.length === 0) {
    return (
      <div className="card">
        <h2>Solicitações</h2>
        Nenhuma solicitação encontrada.
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Solicitações</h2>
      <div className="table-wrapper">
        <table className="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Título</th>
            <th>Categoria</th>
            <th>Prioridade</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {solicitacoes.map((item) => {
            const nextStatus = STATUS_FLOW[item.status];
            return (
              <tr key={item.id}>
                <td>#{item.id}</td>
                <td>{item.titulo}</td>
                <td>{item.categoria}</td>
                <td>
                  <span className={`badge ${PRIORITY_CLASSES[item.prioridade]}`}>
                    {item.prioridade}
                  </span>
                </td>
                <td>
                  <span className={`badge ${STATUS_CLASSES[item.status]}`}>
                    {item.status}
                  </span>
                </td>
                <td>
                  <div className="actions-group">
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => onSelect(item)}
                    >
                      Consultar
                    </button>
                    {nextStatus && (
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        title={`Avançar para ${nextStatus}`}
                        onClick={() => onAdvanceStatus(item.id, nextStatus)}
                      >
                        {NEXT_ACTION_LABEL[item.status] || 'Avançar'}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        </table>
      </div>
    </div>
  );
}
