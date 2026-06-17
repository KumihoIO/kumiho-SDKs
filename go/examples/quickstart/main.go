// Quickstart for the Kumiho Go SDK.
//
//	KUMIHO_SERVER_ENDPOINT=localhost:8080 go run ./examples/quickstart
//
// With cached credentials (`kumiho-cli login`) discovery is automatic:
//
//	go run ./examples/quickstart
package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"os"

	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
)

func main() {
	ctx := context.Background()

	var (
		client *kumiho.Client
		err    error
	)
	if ep := os.Getenv("KUMIHO_SERVER_ENDPOINT"); ep != "" {
		client, err = kumiho.Connect(ctx, ep)
	} else {
		client, err = kumiho.Auto(ctx)
	}
	if err != nil {
		log.Fatalf("connect: %v", err)
	}
	defer client.Close()

	// Project -> space -> item -> revision -> artifact.
	project, err := client.CreateProject(ctx, "go-demo", "Kumiho Go SDK demo")
	if err != nil {
		log.Fatalf("create project: %v", err)
	}
	fmt.Printf("project: %s (%s)\n", project.Name, project.ProjectID)

	space, err := project.CreateSpace(ctx, "characters", "")
	if err != nil {
		log.Fatal(err)
	}
	hero, err := space.CreateItem(ctx, "hero", "model")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("item:    %s\n", hero.Kref)

	rev, err := hero.CreateRevision(ctx, nil, 0)
	if err != nil {
		log.Fatal(err)
	}
	if _, err := rev.CreateArtifact(ctx, "mesh", "/assets/hero.fbx", nil); err != nil {
		log.Fatal(err)
	}
	if err := rev.SetDefaultArtifact(ctx, "mesh"); err != nil {
		log.Fatal(err)
	}
	if err := rev.Tag(ctx, "approved"); err != nil {
		log.Fatal(err)
	}
	fmt.Printf("revision %d tagged, default artifact set\n", rev.Number)

	// Dependency edge + impact analysis.
	tex, _ := space.CreateItem(ctx, "skin", "texture")
	texRev, _ := tex.CreateRevision(ctx, nil, 0)
	if _, err := rev.CreateEdge(ctx, texRev, kumiho.EdgeDependsOn, nil); err != nil {
		log.Fatal(err)
	}
	impacted, _ := texRev.AnalyzeImpact(ctx, nil, 10, 100)
	fmt.Printf("%d revisions depend on the texture\n", len(impacted))

	// Full-text search.
	hits, err := client.Search(ctx, "hero", kumiho.SearchOptions{ContextFilter: "go-demo"})
	if err != nil {
		log.Fatal(err)
	}
	for _, h := range hits.Items {
		fmt.Printf("hit: %s (score %.2f)\n", h.Item.Kref, h.Score)
	}

	// Tail one live event (best-effort).
	if stream, err := client.EventStream(ctx, "revision.*", "", "", "", false); err == nil {
		ev, err := stream.Recv()
		if err == nil {
			fmt.Printf("event: %s -> %s\n", ev.RoutingKey, ev.Kref)
		} else if !errors.Is(err, io.EOF) {
			fmt.Printf("event stream ended: %v\n", err)
		}
	}
}
