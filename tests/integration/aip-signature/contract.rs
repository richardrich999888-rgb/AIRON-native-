//! Test-only consumer of an independently checked-out AIP crypto crate.
//! No AIP source is copied into AIRON and this binary is not a runtime dependency.
use std::{env, fs, path::PathBuf};
use aip_crypto::{sign_ed25519_raw, verify_ed25519_raw};

fn main() {
    let root = PathBuf::from(env::args().nth(1).expect("vector directory required"));
    let count: usize = fs::read_to_string(root.join("count.txt")).unwrap().trim().parse().unwrap();
    assert!((1..=1000).contains(&count));
    let key = fs::read(root.join("public.key")).unwrap();
    assert_eq!(key.len(), 32);
    let mut negatives = 0;
    for i in 0..count {
        let message = fs::read(root.join(format!("record-{i}.bytes"))).unwrap();
        assert!(!message.is_empty() && message.len() <= 1_048_576);
        let signature: [u8; 64] = fs::read(root.join(format!("record-{i}.sig"))).unwrap().try_into().unwrap();
        assert!(verify_ed25519_raw(&key, &message, &signature), "real AIRON signature {i}");
        let mut changed_message = message.clone();
        changed_message[0] ^= 1;
        assert!(!verify_ed25519_raw(&key, &changed_message, &signature));
        let mut changed_signature = signature;
        changed_signature[0] ^= 1;
        assert!(!verify_ed25519_raw(&key, &message, &changed_signature));
        let mut wrong_key = key.clone();
        wrong_key[0] ^= 1;
        assert!(!verify_ed25519_raw(&wrong_key, &message, &signature));
        negatives += 3;
    }
    // Public, fixed interoperability test seed. Never an authority/deployment key.
    let message = fs::read(root.join("roundtrip.bytes")).unwrap();
    let signature = sign_ed25519_raw(&[52u8; 32], &message).unwrap();
    let public = fs::read(root.join("roundtrip-public.key")).unwrap();
    assert!(verify_ed25519_raw(&public, &message, &signature));
    fs::write(root.join("roundtrip-aip.sig"), signature).unwrap();
    println!("{{\"real_records_verified\":{count},\"tamper_rejections\":{negatives},\"aip_roundtrip_signed\":true}}");
}
