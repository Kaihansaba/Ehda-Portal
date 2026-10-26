namespace Ehda_Portal.Models
{
    public class BloodRequest
    {
        public int RequestId { get; set; }
        public int SeekerId { get; set; }
        public int? DonorId { get; set; }
        public string BloodType { get; set; } = string.Empty;
        public string Status { get; set; } = "Pending";
        public DateTime RequestDate { get; set; } = DateTime.Now;
    }
}