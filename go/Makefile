# Code generation for the Kumiho Go SDK.
#
# Requires: protoc, protoc-gen-go, protoc-gen-go-grpc on PATH.
#   go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
#   go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

PKG := github.com/KumihoIO/kumiho-SDKs/go/kumihopb

.PHONY: generate test vet build tidy

generate:
	mkdir -p kumihopb
	protoc -I proto \
		--go_out=kumihopb --go_opt=paths=source_relative \
		--go_opt=Mkumiho.proto=$(PKG) \
		--go-grpc_out=kumihopb --go-grpc_opt=paths=source_relative \
		--go-grpc_opt=Mkumiho.proto=$(PKG) \
		kumiho.proto

tidy:
	go mod tidy

build:
	go build ./...

vet:
	go vet ./...

test:
	go test ./...
