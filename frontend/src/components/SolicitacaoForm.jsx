import { useState } from 'react';
import { criarSolicitacao } from '../services/api';

export default function SolicitacaoForm({ onCreated }) {
  const [titulo, setTitulo] = useState('');
  const [descricao, setDescricao] = useState('');
  const [categoria, setCategoria] = useState('');
  const [prioridade, setPrioridade] = useState('média');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await criarSolicitacao({
        titulo,
        descricao,
        categoria,
        prioridade,
      });
      setTitulo('');
      setDescricao('');
      setCategoria('');
      setPrioridade('média');
      if (onCreated) {
        onCreated();
      }
    } catch (data) {
      setError(data.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Nova Solicitação</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="titulo">Título</label>
          <input
            id="titulo"
            type="text"
            value={titulo}
            onChange={(event) => setTitulo(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="descricao">Descrição</label>
          <textarea
            id="descricao"
            value={descricao}
            onChange={(event) => setDescricao(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="categoria">Categoria</label>
          <input
            id="categoria"
            type="text"
            value={categoria}
            onChange={(event) => setCategoria(event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="prioridade">Prioridade</label>
          <select
            id="prioridade"
            value={prioridade}
            onChange={(event) => setPrioridade(event.target.value)}
          >
            <option value="baixa">baixa</option>
            <option value="média">média</option>
            <option value="alta">alta</option>
          </select>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Enviando...' : 'Criar Solicitação'}
        </button>
      </form>
    </div>
  );
}
