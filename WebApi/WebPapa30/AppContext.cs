using Microsoft.EntityFrameworkCore;
using WebPapa30.Models;

namespace WebPapa30
{
    public class AppContext : DbContext
    {
        public DbSet<Customer> Customers { get; set; }
        public DbSet<Tender> Tenders { get; set; }
        public DbSet<Winner> Winners { get; set; }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseNpgsql("Host=localhost;Port=5432;Database=usersdb2;Username=postgres;Password=password");
        }
    }
}