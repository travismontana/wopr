FROM golang:1.26 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download          # ← cached layer, only reruns if go.sum changes
COPY . .
RUN CGO_ENABLED=0 go build -o myapp .

FROM scratch
COPY --from=builder /app/woprmodel /myapp
ENTRYPOINT ["/myapp"]