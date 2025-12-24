  # Initialize FastAPI app
  app = FastAPI()

  # Instrument FastAPI with OpenTelemetry
  FastAPIInstrumentor.instrument_app(app)

  