import React, { useEffect } from 'react';

const STATUS_OPTIONS = ['Aberta', 'Em andamento', 'Concluída'];

export default function SolicitacaoDetailModal({ solicitacao, onClose, onChangeStatus }) {
  useEffect(() => {
    if (!solicitacao) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [solicitacao, onClose]);

  if (!solicitacao) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Consulta da Solicitação #{solicitacao.id}</h2>
        <p><strong>Título:</strong> {solicitacao.titulo}</p>
        <p><strong>Descrição:</strong> {solicitacao.descricao}</p>
        <p><strong>Categoria:</strong> {solicitacao.categoria}</p>
        <p><strong>Prioridade:</strong> {solicitacao.prioridade}</p>
        <p><strong>Status atual:</strong> {solicitacao.status}</p>
        <p>
          <strong>Data de criação:</strong>{' '}
          {new Date(solicitacao.created_at).toLocaleString('pt-BR')}
        </p>

        <div className="modal-actions">
          {STATUS_OPTIONS.map((target) => {
            const isCurrent = target === solicitacao.status;
            return (
              <button
                key={target}
                type="button"
                className={isCurrent ? 'btn btn-primary btn-sm' : 'btn btn-secondary btn-sm'}
                disabled={isCurrent}
                onClick={() => onChangeStatus(solicitacao.id, target)}
              >
                {isCurrent ? `Atual: ${target}` : `Mover para ${target}`}
              </button>
            );
          })}
          <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
