import React, { useState } from 'react';

export default function SolicitacaoFilters({
  status,
  prioridade,
  busca,
  onStatusChange,
  onPrioridadeChange,
  onBuscaChange,
  onClear,
  onLookupById,
}) {
  const [lookupId, setLookupId] = useState('');

  function handleLookupSubmit(e) {
    e.preventDefault();
    if (!lookupId.trim()) return;
    onLookupById(lookupId.trim());
  }

  return (
    <div className="card">
      <h2>Consulta e Filtros</h2>
      <div className="filters-bar">
        <div className="form-group">
          <label htmlFor="filter-busca">Pesquisar por nome</label>
          <input
            id="filter-busca"
            type="text"
            placeholder="Ex: estoque, mouse..."
            value={busca}
            onChange={(e) => onBuscaChange(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="filter-status">Status</label>
          <select
            id="filter-status"
            value={status}
            onChange={(e) => onStatusChange(e.target.value)}
          >
            <option value="">Todos</option>
            <option value="Aberta">Aberta</option>
            <option value="Em andamento">Em andamento</option>
            <option value="Concluída">Concluída</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="filter-prioridade">Prioridade</label>
          <select
            id="filter-prioridade"
            value={prioridade}
            onChange={(e) => onPrioridadeChange(e.target.value)}
          >
            <option value="">Todas</option>
            <option value="baixa">baixa</option>
            <option value="média">média</option>
            <option value="alta">alta</option>
          </select>
        </div>

        <button type="button" className="btn btn-secondary" onClick={onClear}>
          Limpar filtros
        </button>

        {onLookupById && (
          <form className="lookup-form" onSubmit={handleLookupSubmit}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="lookup-id">Consultar por ID</label>
              <input
                id="lookup-id"
                type="number"
                min="1"
                placeholder="Ex: 1"
                value={lookupId}
                onChange={(e) => setLookupId(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Consultar
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
