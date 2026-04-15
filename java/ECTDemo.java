public class ECTDemo {
    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("ECT LEDGER DEMO - Energy Credit Token System");
        System.out.println("============================================================");

        ECTLedger ledger = new ECTLedger();

        System.out.println("\n--- Issuing Tokens ---");
        ledger.issueToken("FAR001", 850, 0.3476, 32.5825);
        ledger.issueToken("FAR002", 650, -0.6067, 30.6565);
        ledger.issueToken("FAR003", 420, 2.7747, 32.2995);

        System.out.println("\n--- Token Status ---");
        ledger.showTokens("FAR001");
        ledger.showTokens("FAR002");

        System.out.println("\n--- Redeeming Token at Valid Location ---");
        boolean success = ledger.redeemToken("FAR001", "PN001", 0.3476, 32.5825);
        System.out.println("Redeem at valid pump (5km): " + (success ? "SUCCESS" : "FAILED"));

        System.out.println("\n--- Attempting Invalid Redemption ---");
        success = ledger.redeemToken("FAR001", "PN002", 0.5000, 33.0000);
        System.out.println("Redeem at distant pump (50km): " + (success ? "SUCCESS" : "FAILED"));

        System.out.println("\n--- Ledger Stats ---");
        ledger.printStats();

        System.out.println("\n--- Sample Token JSON ---");
        ledger.issueToken("FAR999", 750, 1.5, 32.0);
        for (EnergyCreditToken sample : ledger.farmerTokens.get("FAR999")) {
        System.out.println("{");
        System.out.println("  \"token_id\": \"" + sample.tokenId + "\",");
        System.out.println("  \"farmer_id\": \"" + sample.farmerId + "\",");
        System.out.println("  \"yps_score\": " + sample.ypsScore + ",");
        System.out.println("  \"kwh_allocated\": " + sample.kwhAllocated + ",");
        System.out.println("  \"expires_at\": " + sample.expiresAt + ",");
        System.out.println("  \"gps_lock\": \"" + sample.gpsLat + "," + sample.gpsLon + "\",");
        System.out.println("  \"issuer_sig\": \"" + sample.issuerSig + "\",");
        System.out.println("  \"redeemed\": " + sample.redeemed);
        System.out.println("}");
        break; }

        System.out.println("\n============================================================");
        System.out.println("ECT Ledger Demo Complete!");
        System.out.println("============================================================");
    }
}

class ECTLedger {
    java.util.Map<String, java.util.List<EnergyCreditToken>> farmerTokens = new java.util.HashMap<>();
    java.util.Map<String, EnergyCreditToken> tokenIndex = new java.util.HashMap<>();

    public void issueToken(String farmerId, int ypsScore, double gpsLat, double gpsLon) {
        double kwh = calculateKwhFromYps(ypsScore);
        String tokenId = "ECT" + System.currentTimeMillis();
        
        EnergyCreditToken token = new EnergyCreditToken(tokenId, farmerId, ypsScore, kwh, gpsLat, gpsLon);
        
        farmerTokens.computeIfAbsent(farmerId, k -> new java.util.ArrayList<>()).add(token);
        tokenIndex.put(tokenId, token);
        
        String category = ypsScore >= 800 ? "Excellent" : ypsScore >= 600 ? "Good" : ypsScore >= 400 ? "Fair" : "Low";
        System.out.printf("[ISSUE] %s: YPS=%d (%s) -> %.1f kWh%n", farmerId, ypsScore, category, kwh);
    }

    private double calculateKwhFromYps(int yps) {
        if (yps >= 800) return 50.0;
        if (yps >= 600) return 30.0;
        if (yps >= 400) return 15.0;
        return 5.0;
    }

    public boolean redeemToken(String farmerId, String pumpNodeId, double pumpLat, double pumpLon) {
        java.util.List<EnergyCreditToken> tokens = farmerTokens.get(farmerId);
        if (tokens == null) return false;
        
        for (EnergyCreditToken t : tokens) {
            if (!t.redeemed && !t.isExpired()) {
                if (t.canRedeemAt(pumpNodeId, pumpLat, pumpLon)) {
                    t.redeem(pumpNodeId);
                    System.out.println("[REDEEM] " + farmerId + " at pump " + pumpNodeId + ": SUCCESS");
                    return true;
                }
            }
        }
        System.out.println("[REDEEM] " + farmerId + " at pump " + pumpNodeId + ": FAILED (expired or too far)");
        return false;
    }

    public void showTokens(String farmerId) {
        java.util.List<EnergyCreditToken> tokens = farmerTokens.get(farmerId);
        if (tokens != null) {
            for (EnergyCreditToken t : tokens) {
                System.out.printf("  %s: kWh=%.1f, redeemed=%b, expired=%b%n", 
                    t.tokenId, t.kwhAllocated, t.redeemed, t.isExpired());
            }
        }
    }

    public void printStats() {
        int total = tokenIndex.size();
        int active = 0, expired = 0, redeemed = 0;

        for (EnergyCreditToken t : tokenIndex.values()) {
            if (t.redeemed) redeemed++;
            else if (t.isExpired()) expired++;
            else active++;
        }

        System.out.println("Total tokens issued: " + total);
        System.out.println("Active tokens: " + active);
        System.out.println("Expired tokens: " + expired);
        System.out.println("Redeemed tokens: " + redeemed);
    }
}

class EnergyCreditToken {
    String tokenId;
    String farmerId;
    int ypsScore;
    double kwhAllocated;
    long issuedAt;
    long expiresAt;
    double gpsLat;
    double gpsLon;
    String issuerSig;
    boolean redeemed;
    String pumpNodeId;

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
        this.issuerSig = Integer.toHexString((tokenId + farmerId + ypsScore).hashCode());
    }

    public boolean isExpired() {
        return System.currentTimeMillis() / 1000 > expiresAt;
    }

    public boolean canRedeemAt(String pumpNodeId, double pumpLat, double pumpLon) {
        if (isExpired() || redeemed) return false;
        
        double distance = calculateDistance(gpsLat, gpsLon, pumpLat, pumpLon);
        System.out.println("  Distance check: " + String.format("%.2f", distance) + " km (limit: 5km)");
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

    public void redeem(String pumpNodeId) {
        this.redeemed = true;
        this.pumpNodeId = pumpNodeId;
    }
}