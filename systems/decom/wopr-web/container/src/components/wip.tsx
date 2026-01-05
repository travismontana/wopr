// src/routes/wip.tsx (or index.tsx for unfinished routes)

export default function WorkInProgress() {
  return (
    <article className="page wip-page">
      <div className="wip-content">
        <img 
          src="/assets/construction.gif" 
          alt="Under construction"
          className="wip-gif"
        />
        <h1>Work in Progress</h1>
        <p className="wip-message">
          This feature is currently under construction.
          <br />
          Check back soon!
        </p>
      </div>
    </article>
  );
}