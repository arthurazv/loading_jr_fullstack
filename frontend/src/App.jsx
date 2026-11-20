import { useState, useEffect } from 'react';
import { listarSolicitacoes, obterSolicitacao, atualizarStatus } from './services/api';
import SolicitacaoForm from './components/SolicitacaoForm';
import SolicitacaoFilters from './components/SolicitacaoFilters';
import SolicitacaoList from './components/SolicitacaoList';
import SolicitacaoDetailModal from './components/SolicitacaoDetailModal';

const STATUS_LABELS = ['Aberta', 'Em andamento', 'Concluída'];

export default function App() {
  const [solicitacoes, setSolicitacoes] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [prioridadeFilter, setPrioridadeFilter] = useState('');
  const [buscaFilter, setBuscaFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  async function refresh(silent = false) {
    if (!silent) {
      setLoading(true);
    }
    try {
      const data = await listarSolicitacoes({
        status: statusFilter,
        prioridade: prioridadeFilter,
        busca: buscaFilter,
      });
      setSolicitacoes(data);
      setSelected((prev) => {
        if (!prev) return null;
        const updated = data.find((s) => s.id === prev.id);
        return updated || prev;
      });
    } catch (error) {
      if (!silent) {
        setFeedback({ type: 'error', message: error.message });
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }

  useEffect(() => {
    refresh();
    const intervalId = setInterval(() => {
      refresh(true);
    }, 3000);
    const handleFocus = () => refresh(true);
    window.addEventListener('focus', handleFocus);
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('focus', handleFocus);
    };
  }, [statusFilter, prioridadeFilter, buscaFilter]);

  async function handleStatusChange(id, newStatus) {
    try {
      const updatedItem = await atualizarStatus(id, newStatus);
      setSolicitacoes((prev) =>
        prev.map((item) => (item.id === id ? updatedItem : item))
      );
      setSelected((prev) => (prev && prev.id === id ? updatedItem : prev));
      setFeedback({ type: 'success', message: `Status atualizado para "${updatedItem.status}".` });
      await refresh();
    } catch (error) {
      setFeedback({ type: 'error', message: error.message });
    }
  }

  async function handleLookupById(id) {
    try {
      const item = await obterSolicitacao(id);
      setSelected(item);
    } catch (error) {
      setFeedback({ type: 'error', message: error.message });
    }
  }

  function closeFeedback() {
    setFeedback(null);
  }

  const stats = solicitacoes.reduce(
    (acc, item) => {
      acc.total += 1;
      if (STATUS_LABELS.includes(item.status)) {
        acc[item.status] += 1;
      }
      return acc;
    },
    { total: 0, Aberta: 0, 'Em andamento': 0, Concluída: 0 }
  );

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <div>
            <h1>Central de Solicitações</h1>
            <p>Registro, filtragem e acompanhamento de demandas internas</p>
          </div>
        </div>
      </header>

      <div className="container">
        {feedback && (
          <div className={`alert alert-${feedback.type}`}>
            <span>{feedback.message}</span>
            <button className="close" onClick={closeFeedback} aria-label="Fechar alerta">
              ×
            </button>
          </div>
        )}

        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-card stat-card--aberta">
            <span className="stat-label">Abertas</span>
            <span className="stat-value">{stats.Aberta}</span>
          </div>
          <div className="stat-card stat-card--andamento">
            <span className="stat-label">Em andamento</span>
            <span className="stat-value">{stats['Em andamento']}</span>
          </div>
          <div className="stat-card stat-card--concluida">
            <span className="stat-label">Concluídas</span>
            <span className="stat-value">{stats.Concluída}</span>
          </div>
        </div>

        <div className="grid-layout">
          <SolicitacaoForm
            onCreated={() => {
              setFeedback({ type: 'success', message: 'Solicitação criada com sucesso!' });
              refresh();
            }}
          />

          <main>
          <SolicitacaoFilters
            status={statusFilter}
            prioridade={prioridadeFilter}
            busca={buscaFilter}
            onStatusChange={setStatusFilter}
            onPrioridadeChange={setPrioridadeFilter}
            onBuscaChange={setBuscaFilter}
            onLookupById={handleLookupById}
            onClear={() => {
              setStatusFilter('');
              setPrioridadeFilter('');
              setBuscaFilter('');
            }}
          />

          <SolicitacaoList
            solicitacoes={solicitacoes}
            selected={selected}
            onSelect={setSelected}
            loading={loading}
            onAdvanceStatus={handleStatusChange}
          />
        </main>
      </div>

      <SolicitacaoDetailModal
        solicitacao={selected}
        onClose={() => setSelected(null)}
        onChangeStatus={handleStatusChange}
      />
      </div>
    </>
  );
}
