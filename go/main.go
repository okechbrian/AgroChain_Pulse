package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"time"
)

type YPSRecord struct {
	FarmerID   string `json:"farmer_id"`
	YPSScore   int    `json:"yps_score"`
	Timestamp  string `json:"timestamp"`
	DataHash   string `json:"data_hash"`
	RecordHash string `json:"record_hash"`
}

type BlockchainLite struct {
	Chain       []YPSRecord
	StoragePath string
}

func NewBlockchainLite(path string) *BlockchainLite {
	bc := &BlockchainLite{
		StoragePath: path,
	}
	bc.loadChain()
	return bc
}

func (bc *BlockchainLite) loadChain() {
	data, err := os.ReadFile(bc.StoragePath)
	if err != nil {
		bc.Chain = []YPSRecord{}
		return
	}
	json.Unmarshal(data, &bc.Chain)
}

func (bc *BlockchainLite) saveChain() {
	data, _ := json.MarshalIndent(bc.Chain, "", "  ")
	os.WriteFile(bc.StoragePath, data, 0644)
}

func hashData(data map[string]interface{}) string {
	str, _ := json.Marshal(data)
	hash := sha256.Sum256(str)
	return fmt.Sprintf("%x", hash[:8])
}

func calcRecordHash(farmerID string, yps int, timestamp string, dataHash string, prevHash string) string {
	raw := fmt.Sprintf("%s%d%s%s%s", farmerID, yps, timestamp, dataHash, prevHash)
	hash := sha256.Sum256([]byte(raw))
	return fmt.Sprintf("%x", hash[:8])
}

func (bc *BlockchainLite) AddYPSRecord(farmerID string, sensorData map[string]interface{}, ypsScore int) YPSRecord {
	timestamp := time.Now().Format(time.RFC3339)
	dataHash := hashData(sensorData)

	prevHash := "0000000000000000"
	if len(bc.Chain) > 0 {
		prevHash = bc.Chain[len(bc.Chain)-1].RecordHash
	}

	recordHash := calcRecordHash(farmerID, ypsScore, timestamp, dataHash, prevHash)

	record := YPSRecord{
		FarmerID:   farmerID,
		YPSScore:   ypsScore,
		Timestamp:  timestamp,
		DataHash:   dataHash,
		RecordHash: recordHash,
	}

	bc.Chain = append(bc.Chain, record)
	bc.saveChain()

	return record
}

func (bc *BlockchainLite) GetYPS(farmerID string) *YPSRecord {
	for i := len(bc.Chain) - 1; i >= 0; i-- {
		if bc.Chain[i].FarmerID == farmerID {
			return &bc.Chain[i]
		}
	}
	return nil
}

func (bc *BlockchainLite) VerifyChain() bool {
	for i := 1; i < len(bc.Chain); i++ {
		prev := bc.Chain[i-1]
		curr := bc.Chain[i]
		expected := calcRecordHash(curr.FarmerID, curr.YPSScore, curr.Timestamp, curr.DataHash, prev.RecordHash)
		if curr.RecordHash != expected {
			return false
		}
	}
	return true
}

func (bc *BlockchainLite) GetStats() map[string]interface{} {
	unique := make(map[string]bool)
	for _, r := range bc.Chain {
		unique[r.FarmerID] = true
	}

	latestHash := "0000000000000000"
	if len(bc.Chain) > 0 {
		latestHash = bc.Chain[len(bc.Chain)-1].RecordHash
	}

	return map[string]interface{}{
		"total_records":  len(bc.Chain),
		"unique_farmers": len(unique),
		"verified":       bc.VerifyChain(),
		"latest_hash":    latestHash,
	}
}

func main() {
	fmt.Println("============================================================")
	fmt.Println("BLOCKCHAIN-LITE (Go) - Append-Only Log with SHA-256")
	fmt.Println("============================================================")

	chain := NewBlockchainLite("data/chain_go.json")

	sampleData := []map[string]interface{}{
		{"farmer_id": "FAR001", "soil_moisture": 45.2, "temperature": 24.5},
		{"farmer_id": "FAR002", "soil_moisture": 38.7, "temperature": 26.1},
		{"farmer_id": "FAR001", "soil_moisture": 52.3, "temperature": 23.8},
	}

	fmt.Println("\n--- Adding YPS Records ---")
	for _, data := range sampleData {
		yps := len(data["farmer_id"].(string)) * 100
		record := chain.AddYPSRecord(data["farmer_id"].(string), data, yps)
		fmt.Printf("[ADD] %s -> YPS: %d | Hash: %s\n", record.FarmerID, record.YPSScore, record.RecordHash)
	}

	fmt.Println("\n--- Chain Stats ---")
	stats := chain.GetStats()
	fmt.Printf("Total Records: %v\n", stats["total_records"])
	fmt.Printf("Unique Farmers: %v\n", stats["unique_farmers"])
	fmt.Printf("Chain Verified: %v\n", stats["verified"])
	fmt.Printf("Latest Hash: %v\n", stats["latest_hash"])

	fmt.Println("\n--- Query FAR001 ---")
	rec := chain.GetYPS("FAR001")
	if rec != nil {
		fmt.Printf("Farmer: %s\n", rec.FarmerID)
		fmt.Printf("YPS: %d\n", rec.YPSScore)
		fmt.Printf("Timestamp: %s\n", rec.Timestamp)
		fmt.Printf("Hash: %s\n", rec.RecordHash)
	}

	fmt.Println("\n============================================================")
	fmt.Println("Go Blockchain-Lite Ready!")
	fmt.Println("============================================================")
}
