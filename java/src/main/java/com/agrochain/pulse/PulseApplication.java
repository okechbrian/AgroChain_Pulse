package com.agrochain.pulse;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@SpringBootApplication
@RestController
@CrossOrigin
public class PulseApplication {

    public static void main(String[] args) {
        SpringApplication.run(PulseApplication.class, args);
    }
}

class ECTLedger {
    private Map<String, List<EnergyCreditToken>> farmerTokens = new HashMap<>();
    private Map<String, EnergyCreditToken> tokenIndex = new HashMap<>();

    public EnergyCreditToken issueToken(String farmerId, int ypsScore, double gpsLat, double gpsLon) {
        double kwh = calculateKwhFromYps(ypsScore);
        String tokenId = "ECT" + System.currentTimeMillis();
        
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
        int active = 0, expired = 0, redeemed = 0;

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
}

class EnergyCreditToken {
    private String tokenId;
    private String farmerId;
    private int ypsScore;
    private double kwhAllocated;
    private long issuedAt;
    private long expiresAt;
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
        this.issuedAt = System.currentTimeMillis() / 1000;
        this.expiresAt = issuedAt + (72 * 3600);
        this.redeemed = false;
        this.issuerSignature = Integer.toHexString((tokenId + farmerId + ypsScore).hashCode());
    }

    public boolean isExpired() {
        return System.currentTimeMillis() / 1000 > expiresAt;
    }

    public boolean canRedeemAt(String pumpNodeId, double pumpLat, double pumpLon) {
        if (isExpired() || redeemed) return false;
        double distance = Math.sqrt(Math.pow((gpsLat - pumpLat) * 111, 2) + 
                                    Math.pow((gpsLon - pumpLon) * 111 * Math.cos(Math.toRadians(gpsLat)), 2));
        return distance <= 5.0;
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
        json.put("issued_at", issuedAt);
        json.put("expires_at", expiresAt);
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
    public long getExpiresAt() { return expiresAt; }
}