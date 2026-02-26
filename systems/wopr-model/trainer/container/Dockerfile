FROM golang:1.26 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o woprmodel ./app/

FROM alpine:3.23 
COPY --from=builder /app/woprmodel /woprmodel
ENTRYPOINT ["/woprmodel"]