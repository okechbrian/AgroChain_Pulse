package com.agrochain.pulse;

import java.time.Instant;
import java.util.*;

public class EnergyCreditToken {
    private String tokenId;
    private String farmerId;
    private int ypsScore;
    private double kwhAllocated;
    private Instant issuedAt;
    private Instant expiresAt;
    private double gpsLat;
    private double gpsLon;
    private String issuerSignature;
    private boolean redeemed;
    private String pumpNodeId;

    public EnergyCreditToken(String tokenId, String farmerId, int ypsScore, 
                             double kwhAllocated, double gpsLat, double gpsLon) {
        this.tokenId = tokenId;
        this.farmerId = farmerId;
        this.ypsScore = ypsScore;
        this.kwhAllocated = kwhAllocated;
        this.gpsLat = gpsLat;
        this.gpsLon = gpsLon;
        this.issuedAt = Instant.now();
        this.expiresAt = issuedAt.plusSeconds(72 * 3600);
        this.redeemed = false;
        this.issuerSignature = generateSignature();
    }

    private String generateSignature() {
        String data = tokenId + farmerId + ypsScore + kwhAllocated + issuedAt.toString();
        return Integer.toHexString(data.hashCode());
    }

    public boolean isExpired() {
        return Instant.now().isAfter(expiresAt);
    }

    public boolean canRedeemAt(String pumpNodeId, double pumpLat, double pumpLon) {
        if (isExpired() || redeemed) return false;
        
        double distance = calculateDistance(gpsLat, gpsLon, pumpLat, pumpLon);
        return distance <= 5.0;
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        double R = 6371;
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                   Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                   Math.sin(dLon/2) * Math.sin(dLon/2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    public boolean redeem(String pumpNodeId, double pumpLat, double pumpLon) {
        if (canRedeemAt(pumpNodeId, pumpLat, pumpLon)) {
            this.redeemed = true;
            this.pumpNodeId = pumpNodeId;
            return true;
        }
        return false;
    }

    public Map<String, Object> toJson() {
        Map<String, Object> json = new LinkedHashMap<>();
        json.put("token_id", tokenId);
        json.put("farmer_id", farmerId);
        json.put("yps_score", ypsScore);
        json.put("kwh_allocated", kwhAllocated);
        json.put("issued_at", issuedAt.toString());
        json.put("expires_at", expiresAt.toString());
        json.put("gps_lock", String.format("%.6f,%.6f", gpsLat, gpsLon));
        json.put("issuer_sig", issuerSignature);
        json.put("redeemed", redeemed);
        if (redeemed) json.put("pump_node_id", pumpNodeId);
        return json;
    }

    public String getTokenId() { return tokenId; }
    public String getFarmerId() { return farmerId; }
    public double getKwhAllocated() { return kwhAllocated; }
    public boolean isRedeemed() { return redeemed; }
    public Instant getExpiresAt() { return expiresAt; }
}

class ECTLedger {
    private Map<String, List<EnergyCreditToken>> farmerTokens;
    private Map<String, EnergyCreditToken> tokenIndex;

    public ECTLedger() {
        this.farmerTokens = new HashMap<>();
        this.tokenIndex = new HashMap<>();
    }

    public EnergyCreditToken issueToken(String farmerId, int ypsScore, double gpsLat, double gpsLon) {
        double kwh = calculateKwhFromYps(ypsScore);
        String tokenId = "ECT" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0,4);
        
        EnergyCreditToken token = new EnergyCreditToken(tokenId, farmerId, ypsScore, kwh, gpsLat, gpsLon);
        
        farmerTokens.computeIfAbsent(farmerId, k -> new ArrayList<>()).add(token);
        tokenIndex.put(tokenId, token);
        
        return token;
    }

    private double calculateKwhFromYps(int yps) {
        if (yps >= 800) return 50.0;
        if (yps >= 600) return 30.0;
        if (yps >= 400) return 15.0;
        return 5.0;
    }

    public boolean redeemToken(String tokenId, String pumpNodeId, double pumpLat, double pumpLon) {
        EnergyCreditToken token = tokenIndex.get(tokenId);
        if (token == null) return false;
        return token.redeem(pumpNodeId, pumpLat, pumpLon);
    }

    public List<EnergyCreditToken> getActiveTokens(String farmerId) {
        List<EnergyCreditToken> active = new ArrayList<>();
        List<EnergyCreditToken> tokens = farmerTokens.get(farmerId);
        if (tokens != null) {
            for (EnergyCreditToken t : tokens) {
                if (!t.isRedeemed() && !t.isExpired()) {
                    active.add(t);
                }
            }
        }
        return active;
    }

    public Map<String, Object> getStats() {
        int total = tokenIndex.size();
        int active = 0;
        int expired = 0;
        int redeemed = 0;

        for (EnergyCreditToken t : tokenIndex.values()) {
            if (t.isRedeemed()) redeemed++;
            else if (t.isExpired()) expired++;
            else active++;
        }

        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("total_tokens_issued", total);
        stats.put("active_tokens", active);
        stats.put("expired_tokens", expired);
        stats.put("redeemed_tokens", redeemed);
        return stats;
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("ECT LEDGER DEMO - Energy Credit Token System");
        System.out.println("============================================================");

        ECTLedger ledger = new ECTLedger();

        System.out.println("\n--- Issuing Tokens ---");
        String[] farmers = {"FAR001", "FAR002", "FAR003"};
        int[] ypsScores = {850, 650, 420};

        for (int i = 0; i < farmers.length; i++) {
            EnergyCreditToken token = ledger.issueToken(farmers[i], ypsScores[i], 0.3476, 32.5825);
            System.out.printf("[ISSUE] %s: YPS=%d -> %.1f kWh | Expires: %s%n", 
                token.getFarmerId(), token.ypsScore, token.getKwhAllocated(), token.getExpiresAt());
        }

        System.out.println("\n--- Redeeming Token ---");
        boolean success = ledger.redeemToken("ECT1", "PN001", 0.3476, 32.5825);
        System.out.println("[REDEEM] Token 1 at pump PN001: " + (success ? "SUCCESS" : "FAILED"));

        System.out.println("\n--- Active Tokens ---");
        for (String farmer : farmers) {
            List<EnergyCreditToken> active = ledger.getActiveTokens(farmer);
            System.out.printf("%s: %d active token(s)%n", farmer, active.size());
        }

        System.out.println("\n--- Ledger Stats ---");
        Map<String, Object> stats = ledger.getStats();
        stats.forEach((k, v) -> System.out.println(k + ": " + v));

        System.out.println("\n--- Sample Token JSON ---");
        EnergyCreditToken sample = ledger.issueToken("FAR999", 750, 1.5, 32.0);
        Map<String, Object> json = sample.toJson();
        System.out.println("{");
        json.forEach((k, v) -> System.out.println("  \"" + k + "\": \"" + v + "\","));
        System.out.println("}");

        System.out.println("\n============================================================");
        System.out.println("ECT Ledger Ready for Spring Boot Integration!");
        System.out.println("============================================================");
    }
}