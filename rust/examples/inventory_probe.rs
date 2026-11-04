use kumiho::Client;
use std::collections::HashSet;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().collect();
    let client = Client::builder()
        .endpoint(&args[1])
        .token("local-audit-placeholder")
        .use_discovery(false)
        .build()
        .await?;
    let root = &args[2];
    let spaces = client.get_child_spaces(root, true, None, None).await?;
    let items = client.get_items(root, "", "", None, None, true).await?;
    assert!(spaces.pagination_present());
    assert_eq!(spaces.has_more(), Some(false));
    assert!(items.pagination_present());
    assert_eq!(items.has_more(), Some(false));
    assert_eq!(spaces.items.len(), 1004);
    assert_eq!(spaces.total_count, Some(1004));
    assert!(spaces.next_cursor.is_none());
    assert_eq!(items.items.len(), 1004);
    assert_eq!(items.total_count, Some(1004));
    assert!(items.next_cursor.is_none());
    let expected_spaces: HashSet<_> = spaces.items.iter().map(|s| s.path.clone()).collect();
    let expected_items: HashSet<_> = items.items.iter().map(|i| i.kref.to_string()).collect();
    let mut ids = Vec::new();
    let mut sizes = Vec::new();
    let mut cursor = None;
    loop {
        let page = client
            .get_child_spaces(root, true, Some(251), cursor)
            .await?;
        assert_eq!(page.total_count, Some(1004));
        sizes.push(page.items.len());
        assert!(page.pagination_present());
        assert_eq!(page.has_more(), Some(page.next_cursor.is_some()));
        ids.extend(page.items.iter().map(|s| s.path.clone()));
        cursor = page.next_cursor;
        if cursor.is_none() {
            break;
        }
    }
    assert_eq!(sizes, vec![251; 4]);
    assert_eq!(ids.len(), 1004);
    assert_eq!(ids.into_iter().collect::<HashSet<_>>(), expected_spaces);
    let mut ids = Vec::new();
    let mut sizes = Vec::new();
    let mut cursor = None;
    loop {
        let page = client
            .get_items(root, "", "", Some(251), cursor, true)
            .await?;
        assert_eq!(page.total_count, Some(1004));
        sizes.push(page.items.len());
        assert!(page.pagination_present());
        assert_eq!(page.has_more(), Some(page.next_cursor.is_some()));
        ids.extend(page.items.iter().map(|i| i.kref.to_string()));
        cursor = page.next_cursor;
        if cursor.is_none() {
            break;
        }
    }
    assert_eq!(sizes, vec![251; 4]);
    assert_eq!(ids.len(), 1004);
    assert_eq!(ids.into_iter().collect::<HashSet<_>>(), expected_items);
    let space = client.get_space(root).await?;
    assert_eq!(
        space
            .get_items_including_deprecated("", "", None, None)
            .await?
            .items
            .len(),
        1004
    );
    println!(
        "{}",
        serde_json::json!({"sdk":"Rust fixed","unpaged_spaces":1004,"unpaged_items":1004,"page_sizes":sizes,"terminal_cursor":null,"total_count":1004,"result":"PASS"})
    );
    Ok(())
}
