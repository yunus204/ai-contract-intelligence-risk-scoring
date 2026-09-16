import { useEffect, useRef, useState } from "react";

import {
  getTaskStatus,
  searchContract,
  uploadContract,
} from "./api";

import "./App.css";


function App() {
  const [selectedFile, setSelectedFile] =
    useState(null);

  const [uploading, setUploading] =
    useState(false);

  const [taskId, setTaskId] =
    useState("");

  const [contractId, setContractId] =
    useState("");

  const [taskStatus, setTaskStatus] =
    useState("");

  const [progress, setProgress] =
    useState(0);

  const [stage, setStage] =
    useState("");

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");

  const [searchQuery, setSearchQuery] =
    useState("");

  const [searching, setSearching] =
    useState(false);

  const [searchResults, setSearchResults] =
    useState([]);

  const pollingRef = useRef(null);


  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(
          pollingRef.current
        );
      }
    };
  }, []);


  const resetAnalysis = () => {
    setTaskId("");
    setContractId("");
    setTaskStatus("");
    setProgress(0);
    setStage("");
    setResult(null);
    setError("");
    setSearchQuery("");
    setSearchResults([]);
  };


  const handleFileChange = (event) => {
    const file =
      event.target.files[0];

    if (!file) {
      return;
    }

    resetAnalysis();
    setSelectedFile(file);
  };


  const pollTask = (id) => {
    if (pollingRef.current) {
      clearInterval(
        pollingRef.current
      );
    }

    pollingRef.current =
      setInterval(async () => {
        try {
          const data =
            await getTaskStatus(id);

          setTaskStatus(
            data.status
          );

          if (
            data.status ===
            "PROCESSING"
          ) {
            setStage(
              data.stage || ""
            );

            setProgress(
              data.progress || 0
            );
          }

          if (
            data.status ===
            "SUCCESS"
          ) {
            clearInterval(
              pollingRef.current
            );

            pollingRef.current =
              null;

            setProgress(100);
            setStage("completed");

            setResult(
              data.result
            );

            setContractId(
              data.result.contract_id
            );

            setUploading(false);
          }

          if (
            data.status ===
            "FAILURE"
          ) {
            clearInterval(
              pollingRef.current
            );

            pollingRef.current =
              null;

            setUploading(false);

            setError(
              data.error ||
                "Contract processing failed."
            );
          }
        } catch (err) {
          console.error(err);

          clearInterval(
            pollingRef.current
          );

          pollingRef.current =
            null;

          setUploading(false);

          setError(
            "Unable to check processing status."
          );
        }
      }, 2000);
  };


  const handleUpload =
    async () => {
      if (!selectedFile) {
        setError(
          "Please select a PDF or DOCX file."
        );

        return;
      }

      try {
        setError("");
        setUploading(true);
        setResult(null);
        setProgress(5);
        setStage("uploading");

        const response =
          await uploadContract(
            selectedFile
          );

        setTaskId(
          response.task_id
        );

        setContractId(
          response.contract_id
        );

        setTaskStatus(
          response.status
        );

        setProgress(10);
        setStage("queued");

        pollTask(
          response.task_id
        );
      } catch (err) {
        console.error(err);

        setUploading(false);

        setError(
          err?.response?.data?.detail ||
            "Unable to upload contract."
        );
      }
    };


  const handleSearch =
    async (event) => {
      event.preventDefault();

      if (!contractId) {
        setError(
          "Analyze a contract before searching."
        );

        return;
      }

      if (!searchQuery.trim()) {
        return;
      }

      try {
        setSearching(true);
        setError("");

        const response =
          await searchContract({
            contractId,
            query:
              searchQuery.trim(),
            topK: 5,
          });

        setSearchResults(
          response.results || []
        );
      } catch (err) {
        console.error(err);

        setError(
          err?.response?.data?.detail ||
            "Semantic search failed."
        );
      } finally {
        setSearching(false);
      }
    };


  const formatStage = (
    value
  ) => {
    if (!value) {
      return "";
    }

    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };


  return (
    <div className="app-shell">

      <header className="topbar">
        <div>
          <div className="brand-mark">
            AI
          </div>

          <div>
            <h1>
              Contract Intelligence
            </h1>

            <p>
              AI-powered contract
              analysis and risk scoring
            </p>
          </div>
        </div>

        <span className="system-badge">
          System Online
        </span>
      </header>


      <main className="main-content">

        <section className="hero">
          <div>
            <p className="eyebrow">
              LEGAL AI PLATFORM
            </p>

            <h2>
              Analyze contracts.
              <br />
              Detect risk.
              <br />
              Search intelligently.
            </h2>

            <p className="hero-copy">
              Upload PDF or Word
              contracts to extract
              entities, identify legal
              clauses, calculate risk,
              and perform semantic
              search.
            </p>
          </div>

          <div className="hero-stat-grid">
            <div className="hero-stat">
              <strong>41</strong>
              <span>
                CUAD clause categories
              </span>
            </div>

            <div className="hero-stat">
              <strong>AI</strong>
              <span>
                RoBERTa + spaCy
              </span>
            </div>

            <div className="hero-stat">
              <strong>NER</strong>
              <span>
                Entity extraction
              </span>
            </div>

            <div className="hero-stat">
              <strong>Vector</strong>
              <span>
                Semantic search
              </span>
            </div>
          </div>
        </section>


        <section className="panel upload-panel">

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                CONTRACT ANALYSIS
              </p>

              <h3>
                Upload a contract
              </h3>
            </div>

            <span className="file-support">
              PDF / DOCX
            </span>
          </div>


          <div className="upload-area">

            <input
              type="file"
              id="contractFile"
              accept=".pdf,.docx"
              onChange={
                handleFileChange
              }
            />

            <label
              htmlFor="contractFile"
              className="file-label"
            >
              <span className="upload-icon">
                ↑
              </span>

              <span>
                {selectedFile
                  ? selectedFile.name
                  : "Choose contract file"}
              </span>

              <small>
                PDF or Microsoft Word
                document
              </small>
            </label>


            <button
              className="primary-button"
              onClick={
                handleUpload
              }
              disabled={
                uploading ||
                !selectedFile
              }
            >
              {uploading
                ? "Analyzing..."
                : "Analyze Contract"}
            </button>
          </div>


          {error && (
            <div className="error-box">
              {error}
            </div>
          )}


          {(uploading ||
            taskStatus ===
              "SUCCESS") && (
            <div className="progress-card">

              <div className="progress-info">
                <div>
                  <span>
                    Processing Status
                  </span>

                  <strong>
                    {formatStage(
                      stage ||
                        taskStatus
                    )}
                  </strong>
                </div>

                <strong>
                  {progress}%
                </strong>
              </div>

              <div className="progress-track">
                <div
                  className="progress-bar"
                  style={{
                    width:
                      `${progress}%`,
                  }}
                />
              </div>

              {taskId && (
                <small>
                  Task ID: {taskId}
                </small>
              )}
            </div>
          )}

        </section>


        {result && (
          <>
            <section className="summary-grid">

              <div className="panel metric-card risk-card">
                <span>
                  Overall Risk Score
                </span>

                <strong>
                  {
                    result
                      ?.risk_analysis
                      ?.risk_score
                  }
                </strong>

                <div
                  className={`risk-pill ${
                    result
                      ?.risk_analysis
                      ?.risk_level || ""
                  }`}
                >
                  {
                    result
                      ?.risk_analysis
                      ?.risk_level
                  } Risk
                </div>
              </div>


              <div className="panel metric-card">
                <span>
                  Detected Clauses
                </span>

                <strong>
                  {
                    result
                      ?.clause_analysis
                      ?.detected_clauses
                      ?.length || 0
                  }
                </strong>

                <small>
                  CUAD categories
                </small>
              </div>


              <div className="panel metric-card">
                <span>
                  Vector Chunks
                </span>

                <strong>
                  {
                    result
                      ?.vector_index
                      ?.chunks || 0
                  }
                </strong>

                <small>
                  Indexed in Pinecone
                </small>
              </div>


              <div className="panel metric-card">
                <span>
                  Word Count
                </span>

                <strong>
                  {result.word_count}
                </strong>

                <small>
                  {
                    result.extraction_method
                  }
                </small>
              </div>

            </section>


            <section className="dashboard-grid">

              <div className="panel">

                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      ENTITY EXTRACTION
                    </p>

                    <h3>
                      Contract entities
                    </h3>
                  </div>
                </div>


                <EntityGroup
                  title="Organizations"
                  values={
                    result
                      ?.entities
                      ?.organizations
                  }
                />

                <EntityGroup
                  title="Dates"
                  values={
                    result
                      ?.entities
                      ?.dates
                  }
                />

                <EntityGroup
                  title="Money"
                  values={
                    result
                      ?.entities
                      ?.money
                  }
                />

                <EntityGroup
                  title="Jurisdictions"
                  values={
                    result
                      ?.entities
                      ?.jurisdictions
                  }
                />

                <EntityGroup
                  title="Persons"
                  values={
                    result
                      ?.entities
                      ?.persons
                  }
                />

              </div>


              <div className="panel">

                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      RISK ENGINE
                    </p>

                    <h3>
                      Highest risk factors
                    </h3>
                  </div>
                </div>


                <div className="risk-list">

                  {result
                    ?.risk_analysis
                    ?.risk_factors
                    ?.length ? (
                    result
                      .risk_analysis
                      .risk_factors
                      .map(
                        (
                          factor,
                          index
                        ) => (
                          <div
                            className="risk-item"
                            key={
                              `${factor.clause}-${index}`
                            }
                          >
                            <div>
                              <strong>
                                {
                                  factor.clause
                                }
                              </strong>

                              <span>
                                Confidence{" "}
                                {(
                                  factor.confidence *
                                  100
                                ).toFixed(
                                  1
                                )}
                                %
                              </span>
                            </div>

                            <strong>
                              +
                              {
                                factor.risk_contribution
                              }
                            </strong>
                          </div>
                        )
                      )
                  ) : (
                    <p className="empty-state">
                      No risk factors
                      detected.
                    </p>
                  )}

                </div>

              </div>

            </section>


            <section className="panel">

              <div className="section-heading">
                <div>
                  <p className="eyebrow">
                    CLAUSE INTELLIGENCE
                  </p>

                  <h3>
                    Detected clauses
                  </h3>
                </div>

                <span className="file-support">
                  Threshold{" "}
                  {
                    result
                      ?.clause_analysis
                      ?.threshold
                  }
                </span>
              </div>


              <div className="clause-grid">

                {result
                  ?.clause_analysis
                  ?.detected_clauses
                  ?.map(
                    (
                      clause,
                      index
                    ) => (
                      <article
                        className="clause-card"
                        key={
                          `${clause.label_id}-${index}`
                        }
                      >
                        <div className="clause-header">

                          <h4>
                            {
                              clause.clause
                            }
                          </h4>

                          <span>
                            {(
                              clause.confidence *
                              100
                            ).toFixed(
                              1
                            )}
                            %
                          </span>

                        </div>

                        <p>
                          {
                            clause.evidence
                          }
                        </p>

                      </article>
                    )
                  )}

              </div>

            </section>


            <section className="panel search-panel">

              <div className="section-heading">
                <div>
                  <p className="eyebrow">
                    SEMANTIC SEARCH
                  </p>

                  <h3>
                    Ask this contract
                  </h3>
                </div>

                <span className="file-support">
                  Pinecone
                </span>
              </div>


              <form
                className="search-form"
                onSubmit={
                  handleSearch
                }
              >

                <input
                  type="text"
                  value={
                    searchQuery
                  }
                  onChange={(event) =>
                    setSearchQuery(
                      event.target.value
                    )
                  }
                  placeholder="Example: What does this contract say about termination?"
                />

                <button
                  className="primary-button"
                  disabled={
                    searching
                  }
                >
                  {searching
                    ? "Searching..."
                    : "Search"}
                </button>

              </form>


              <div className="search-results">

                {searchResults.map(
                  (
                    item,
                    index
                  ) => (
                    <article
                      className="search-result"
                      key={index}
                    >

                      <div>
                        <strong>
                          Result{" "}
                          {item.rank ||
                            index + 1}
                        </strong>

                        {item.score !==
                          undefined && (
                          <span>
                            Score{" "}
                            {Number(
                              item.score
                            ).toFixed(
                              4
                            )}
                          </span>
                        )}
                      </div>

                      <p>
                        {item.text ||
                          item.content ||
                          item.page_content ||
                          ""}
                      </p>

                    </article>
                  )
                )}

              </div>

            </section>


            <p className="disclaimer">
              AI-generated contract
              analysis is intended for
              review assistance and
              should not be considered
              legal advice.
            </p>
          </>
        )}

      </main>

    </div>
  );
}


function EntityGroup({
  title,
  values = [],
}) {
  return (
    <div className="entity-group">

      <h4>{title}</h4>

      <div className="tag-list">

        {values?.length ? (
          values.map(
            (value, index) => (
              <span
                className="entity-tag"
                key={
                  `${value}-${index}`
                }
              >
                {value}
              </span>
            )
          )
        ) : (
          <span className="empty-tag">
            None detected
          </span>
        )}

      </div>

    </div>
  );
}


export default App;