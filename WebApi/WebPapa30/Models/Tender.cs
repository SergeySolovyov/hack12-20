using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace WebPapa30.Models
{
    public class Tender
    {
        public string RegNumber { get; set; }
        public string CreateDate { get; set; }
        public string Name { get; set; }

        public virtual Winner Winner { get; set; }
    }
}
