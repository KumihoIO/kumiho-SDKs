package kumiho

import (
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// KrefValidationError is returned when a kref URI fails validation.
type KrefValidationError struct{ Msg string }

func (e *KrefValidationError) Error() string { return e.Msg }

// EdgeTypeValidationError is returned when an edge type is malformed.
type EdgeTypeValidationError struct{ Msg string }

func (e *EdgeTypeValidationError) Error() string { return e.Msg }

// ReservedKindError is returned when CreateItem is called with a reserved item
// kind (e.g. "bundle"); use CreateBundle instead. Mirrors Python's
// ReservedKindError so callers can discriminate this case.
type ReservedKindError struct {
	Kind string
	Msg  string
}

func (e *ReservedKindError) Error() string { return e.Msg }

// ProjectLimitError is returned when guardrails block project creation
// (e.g. the tenant's project limit was reached).
type ProjectLimitError struct{ Msg string }

func (e *ProjectLimitError) Error() string { return "project limit reached: " + e.Msg }

// InvalidArgumentError is returned for malformed client-side arguments
// (e.g. a kref that is structurally not an item kref).
type InvalidArgumentError struct{ Msg string }

func (e *InvalidArgumentError) Error() string { return e.Msg }

// KumihoError is the common interface implemented by every error this SDK
// returns, so callers can match them all with a single errors.As. Mirrors
// Python's KumihoError base exception.
//
//	var ke kumiho.KumihoError
//	if errors.As(err, &ke) { /* any kumiho error */ }
type KumihoError interface {
	error
	kumihoError()
}

func (e *KrefValidationError) kumihoError()     {}
func (e *EdgeTypeValidationError) kumihoError() {}
func (e *ReservedKindError) kumihoError()       {}
func (e *ProjectLimitError) kumihoError()       {}
func (e *InvalidArgumentError) kumihoError()    {}

// IsNotFound reports whether err is a gRPC NOT_FOUND status.
func IsNotFound(err error) bool {
	return status.Code(err) == codes.NotFound
}
