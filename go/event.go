package kumiho

import (
	"context"

	pb "github.com/KumihoIO/kumiho-SDKs/go/kumihopb"
	"google.golang.org/grpc"
)

// Event is a real-time notification from the server.
type Event struct {
	RoutingKey string
	Kref       Kref
	Timestamp  string
	Author     string
	Details    map[string]string
	Cursor     string
}

func newEvent(p *pb.Event) *Event {
	return &Event{
		RoutingKey: p.GetRoutingKey(),
		Kref:       krefFromPB(p.GetKref()),
		Timestamp:  p.GetTimestamp(),
		Author:     p.GetAuthor(),
		Details:    p.GetDetails(),
		Cursor:     p.GetCursor(),
	}
}

// EventCapabilities reports event-streaming capabilities for the tenant tier.
type EventCapabilities struct {
	SupportsReplay         bool
	SupportsCursor         bool
	SupportsConsumerGroups bool
	MaxRetentionHours      int64
	MaxBufferSize          int64
	Tier                   string
}

// EventStream is a live subscription to server events. Call Recv repeatedly;
// it returns io.EOF when the server closes the stream.
type EventStream struct {
	stream grpc.ServerStreamingClient[pb.Event]
}

// Recv blocks for the next event.
func (s *EventStream) Recv() (*Event, error) {
	msg, err := s.stream.Recv()
	if err != nil {
		return nil, err
	}
	return newEvent(msg), nil
}

// EventStream subscribes to the server event stream.
//
// cursor and consumerGroup may be ""; fromBeginning replays available history
// (Creator tier+). Filters support wildcards.
func (c *Client) EventStream(ctx context.Context, routingKeyFilter, krefFilter, cursor, consumerGroup string, fromBeginning bool) (*EventStream, error) {
	req := &pb.EventStreamRequest{RoutingKeyFilter: routingKeyFilter, KrefFilter: krefFilter}
	if cursor != "" {
		req.Cursor = &cursor
	}
	if consumerGroup != "" {
		req.ConsumerGroup = &consumerGroup
	}
	if fromBeginning {
		req.StartPosition = &pb.EventStreamRequest_FromBeginning{FromBeginning: true}
	}
	stream, err := c.grpc.EventStream(ctx, req)
	if err != nil {
		return nil, err
	}
	return &EventStream{stream: stream}, nil
}
