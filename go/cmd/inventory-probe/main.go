// Opt-in probe for the isolated CE fixture; never discovers a production endpoint.
package main

import (
	"context"
	"encoding/json"
	"fmt"
	kumiho "github.com/KumihoIO/kumiho-SDKs/go"
	"os"
	"time"
)

func require(ok bool) {
	if !ok {
		panic("inventory compatibility assertion failed")
	}
}
func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	c, err := kumiho.Builder().Endpoint(os.Args[1]).Token("").UseDiscovery(false).Build(ctx)
	if err != nil {
		panic(err)
	}
	defer c.Close()
	root := os.Args[2]
	legacy, err := c.GetChildSpaces(ctx, root, true, 0, "")
	if err != nil {
		panic(err)
	}
	require(len(legacy.Items) == 1004)
	for _, kind := range []string{"spaces", "items"} {
		cursor := ""
		ids := map[string]bool{}
		count := 0
		for {
			var more bool
			if kind == "spaces" {
				p, e := c.GetChildSpacesPaged(ctx, root, true, 251, cursor)
				if e != nil {
					panic(e)
				}
				require(p.PaginationPresent && p.TotalCount == 1004 && len(p.Items) == 251)
				for _, s := range p.Items {
					ids[s.Path] = true
				}
				count += len(p.Items)
				cursor = p.NextCursor
				more = p.HasMore
			} else {
				p, e := c.GetItemsPaged(ctx, root, "", "", 251, cursor, true)
				if e != nil {
					panic(e)
				}
				require(p.PaginationPresent && p.TotalCount == 1004 && len(p.Items) == 251)
				for _, i := range p.Items {
					ids[fmt.Sprint(i.Kref)] = true
				}
				count += len(p.Items)
				cursor = p.NextCursor
				more = p.HasMore
			}
			require(more == (cursor != ""))
			if !more {
				break
			}
		}
		require(count == 1004 && len(ids) == 1004)
	}
	s, err := c.GetSpace(ctx, root)
	if err != nil {
		panic(err)
	}
	all, err := s.GetItemsIncludingDeprecated(ctx, "", "", 0, "")
	if err != nil {
		panic(err)
	}
	require(len(all.Items) == 1004)
	result := map[string]any{"sdk": "Go fixed", "unpaged": 1004, "pages": []int{251, 251, 251, 251}, "metadata_present": true, "result": "PASS"}
	_ = json.NewEncoder(os.Stdout).Encode(result)
}
