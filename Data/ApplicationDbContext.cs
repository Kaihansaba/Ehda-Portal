using Microsoft.EntityFrameworkCore;
using Ehda_Portal.Models;

namespace Ehda_Portal.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<BloodRequest> BloodRequests { get; set; }
    }
}

